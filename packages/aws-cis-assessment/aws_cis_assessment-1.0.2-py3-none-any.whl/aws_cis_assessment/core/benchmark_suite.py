"""Benchmarking suite for performance regression testing."""

import time
import json
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
import logging
from concurrent.futures import ThreadPoolExecutor
import threading

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None

from aws_cis_assessment.core.assessment_engine import AssessmentEngine, ResourceUsageStats
from aws_cis_assessment.core.models import AssessmentResult

logger = logging.getLogger(__name__)


@dataclass
class BenchmarkResult:
    """Result of a single benchmark run."""
    test_name: str
    execution_time_seconds: float
    peak_memory_mb: float
    total_resources_evaluated: int
    compliance_score: float
    error_count: int
    timestamp: datetime
    configuration: Dict[str, Any]
    resource_stats: Optional[ResourceUsageStats] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        if self.resource_stats:
            result['resource_stats'] = asdict(self.resource_stats)
        return result


@dataclass
class BenchmarkSuite:
    """Configuration for a benchmark suite."""
    name: str
    description: str
    tests: List[Dict[str, Any]]
    baseline_file: Optional[str] = None
    regression_threshold: float = 1.2  # 20% performance degradation threshold


class PerformanceBenchmark:
    """Performance benchmarking and regression testing suite."""
    
    def __init__(self, output_dir: str = "benchmarks"):
        """Initialize benchmark suite.
        
        Args:
            output_dir: Directory to store benchmark results
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.results: List[BenchmarkResult] = []
        self._lock = threading.Lock()
    
    def run_benchmark_suite(self, suite: BenchmarkSuite, 
                           iterations: int = 3) -> Dict[str, List[BenchmarkResult]]:
        """Run a complete benchmark suite.
        
        Args:
            suite: BenchmarkSuite configuration
            iterations: Number of iterations per test
            
        Returns:
            Dictionary mapping test names to benchmark results
        """
        logger.info(f"Starting benchmark suite: {suite.name}")
        logger.info(f"Running {len(suite.tests)} tests with {iterations} iterations each")
        
        all_results = {}
        
        for test_config in suite.tests:
            test_name = test_config['name']
            logger.info(f"Running benchmark test: {test_name}")
            
            test_results = []
            for iteration in range(iterations):
                logger.debug(f"  Iteration {iteration + 1}/{iterations}")
                
                try:
                    result = self._run_single_benchmark(test_name, test_config)
                    test_results.append(result)
                    
                    with self._lock:
                        self.results.append(result)
                    
                except Exception as e:
                    logger.error(f"Benchmark test {test_name} iteration {iteration + 1} failed: {e}")
                    # Create error result
                    error_result = BenchmarkResult(
                        test_name=test_name,
                        execution_time_seconds=0.0,
                        peak_memory_mb=0.0,
                        total_resources_evaluated=0,
                        compliance_score=0.0,
                        error_count=1,
                        timestamp=datetime.now(),
                        configuration=test_config
                    )
                    test_results.append(error_result)
            
            all_results[test_name] = test_results
            
            # Log test summary
            if test_results:
                successful_results = [r for r in test_results if r.error_count == 0]
                if successful_results:
                    avg_time = statistics.mean([r.execution_time_seconds for r in successful_results])
                    avg_memory = statistics.mean([r.peak_memory_mb for r in successful_results])
                    logger.info(f"  {test_name}: avg {avg_time:.2f}s, {avg_memory:.1f}MB peak memory")
        
        # Save results
        self._save_benchmark_results(suite, all_results)
        
        # Check for regressions if baseline exists
        if suite.baseline_file:
            self._check_regressions(suite, all_results)
        
        logger.info(f"Benchmark suite {suite.name} completed")
        return all_results
    
    def _run_single_benchmark(self, test_name: str, config: Dict[str, Any]) -> BenchmarkResult:
        """Run a single benchmark test.
        
        Args:
            test_name: Name of the test
            config: Test configuration
            
        Returns:
            BenchmarkResult with performance metrics
        """
        start_time = time.time()
        initial_memory = self._get_memory_usage()
        
        try:
            # Create assessment engine with test configuration
            engine_config = config.get('engine_config', {})
            engine = AssessmentEngine(
                aws_credentials=config.get('aws_credentials'),
                regions=config.get('regions', ['us-east-1']),
                max_workers=engine_config.get('max_workers', 4),
                memory_limit_mb=engine_config.get('memory_limit_mb'),
                enable_resource_monitoring=True
            )
            
            # Mock AWS factory if test data provided
            if 'mock_data' in config:
                self._setup_mock_data(engine, config['mock_data'])
            
            # Run assessment
            implementation_groups = config.get('implementation_groups', ['IG1'])
            result = engine.run_assessment(implementation_groups)
            
            # Get resource statistics
            resource_stats = engine.get_resource_stats()
            
            end_time = time.time()
            execution_time = end_time - start_time
            peak_memory = max(resource_stats.peak_memory_mb, self._get_memory_usage() - initial_memory)
            
            return BenchmarkResult(
                test_name=test_name,
                execution_time_seconds=execution_time,
                peak_memory_mb=peak_memory,
                total_resources_evaluated=result.total_resources_evaluated,
                compliance_score=result.overall_score,
                error_count=len([e for e in engine.progress.errors if e]),
                timestamp=datetime.now(),
                configuration=config,
                resource_stats=resource_stats
            )
            
        except Exception as e:
            end_time = time.time()
            execution_time = end_time - start_time
            
            logger.error(f"Benchmark {test_name} failed: {e}")
            
            return BenchmarkResult(
                test_name=test_name,
                execution_time_seconds=execution_time,
                peak_memory_mb=self._get_memory_usage() - initial_memory,
                total_resources_evaluated=0,
                compliance_score=0.0,
                error_count=1,
                timestamp=datetime.now(),
                configuration=config
            )
    
    def _setup_mock_data(self, engine: AssessmentEngine, mock_data: Dict[str, Any]):
        """Setup mock data for benchmark testing.
        
        Args:
            engine: AssessmentEngine instance
            mock_data: Mock data configuration
        """
        # This would be implemented to setup mock AWS responses
        # for consistent benchmark testing
        pass
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB.
        
        Returns:
            Memory usage in MB
        """
        if PSUTIL_AVAILABLE:
            try:
                process = psutil.Process()
                return process.memory_info().rss / 1024 / 1024
            except:
                pass
        
        # Fallback to resource module
        try:
            import resource
            memory_kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            if hasattr(resource, 'RUSAGE_SELF'):
                # macOS reports in bytes, Linux in KB
                import sys
                if sys.platform == 'darwin':
                    return memory_kb / 1024 / 1024
                else:
                    return memory_kb / 1024
        except:
            pass
        
        return 0.0
    
    def _save_benchmark_results(self, suite: BenchmarkSuite, 
                               results: Dict[str, List[BenchmarkResult]]):
        """Save benchmark results to file.
        
        Args:
            suite: BenchmarkSuite configuration
            results: Benchmark results
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{suite.name}_{timestamp}.json"
        filepath = self.output_dir / filename
        
        # Prepare data for serialization
        output_data = {
            'suite_name': suite.name,
            'suite_description': suite.description,
            'timestamp': datetime.now().isoformat(),
            'results': {}
        }
        
        for test_name, test_results in results.items():
            output_data['results'][test_name] = [result.to_dict() for result in test_results]
        
        # Save to file
        with open(filepath, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        logger.info(f"Benchmark results saved to: {filepath}")
    
    def _check_regressions(self, suite: BenchmarkSuite, 
                          current_results: Dict[str, List[BenchmarkResult]]):
        """Check for performance regressions against baseline.
        
        Args:
            suite: BenchmarkSuite configuration
            current_results: Current benchmark results
        """
        baseline_path = Path(suite.baseline_file)
        if not baseline_path.exists():
            logger.warning(f"Baseline file not found: {baseline_path}")
            return
        
        try:
            with open(baseline_path, 'r') as f:
                baseline_data = json.load(f)
            
            baseline_results = baseline_data.get('results', {})
            regressions = []
            
            for test_name, current_test_results in current_results.items():
                if test_name not in baseline_results:
                    continue
                
                # Calculate average performance for current results
                successful_current = [r for r in current_test_results if r.error_count == 0]
                if not successful_current:
                    continue
                
                current_avg_time = statistics.mean([r.execution_time_seconds for r in successful_current])
                current_avg_memory = statistics.mean([r.peak_memory_mb for r in successful_current])
                
                # Calculate baseline averages
                baseline_test_results = baseline_results[test_name]
                successful_baseline = [r for r in baseline_test_results if r.get('error_count', 0) == 0]
                if not successful_baseline:
                    continue
                
                baseline_avg_time = statistics.mean([r['execution_time_seconds'] for r in successful_baseline])
                baseline_avg_memory = statistics.mean([r['peak_memory_mb'] for r in successful_baseline])
                
                # Check for regressions
                time_ratio = current_avg_time / baseline_avg_time if baseline_avg_time > 0 else 1.0
                memory_ratio = current_avg_memory / baseline_avg_memory if baseline_avg_memory > 0 else 1.0
                
                if time_ratio > suite.regression_threshold:
                    regressions.append({
                        'test': test_name,
                        'metric': 'execution_time',
                        'baseline': baseline_avg_time,
                        'current': current_avg_time,
                        'ratio': time_ratio
                    })
                
                if memory_ratio > suite.regression_threshold:
                    regressions.append({
                        'test': test_name,
                        'metric': 'memory_usage',
                        'baseline': baseline_avg_memory,
                        'current': current_avg_memory,
                        'ratio': memory_ratio
                    })
            
            # Report regressions
            if regressions:
                logger.warning(f"Performance regressions detected:")
                for regression in regressions:
                    logger.warning(f"  {regression['test']} {regression['metric']}: "
                                 f"{regression['ratio']:.2f}x slower "
                                 f"({regression['current']:.2f} vs {regression['baseline']:.2f})")
            else:
                logger.info("No performance regressions detected")
                
        except Exception as e:
            logger.error(f"Failed to check regressions: {e}")
    
    def create_standard_benchmark_suite(self) -> BenchmarkSuite:
        """Create a standard benchmark suite for regression testing.
        
        Returns:
            BenchmarkSuite with standard performance tests
        """
        return BenchmarkSuite(
            name="standard_performance",
            description="Standard performance benchmark suite for regression testing",
            tests=[
                {
                    'name': 'small_account_ig1',
                    'description': 'Small AWS account with IG1 assessment',
                    'regions': ['us-east-1'],
                    'implementation_groups': ['IG1'],
                    'engine_config': {
                        'max_workers': 4,
                        'memory_limit_mb': 512
                    },
                    'mock_data': {
                        'ec2_instances': 50,
                        'iam_users': 20,
                        's3_buckets': 10
                    }
                },
                {
                    'name': 'medium_account_ig2',
                    'description': 'Medium AWS account with IG2 assessment',
                    'regions': ['us-east-1', 'us-west-2'],
                    'implementation_groups': ['IG2'],
                    'engine_config': {
                        'max_workers': 8,
                        'memory_limit_mb': 1024
                    },
                    'mock_data': {
                        'ec2_instances': 200,
                        'iam_users': 100,
                        's3_buckets': 50,
                        'rds_instances': 20
                    }
                },
                {
                    'name': 'large_account_ig3',
                    'description': 'Large AWS account with IG3 assessment',
                    'regions': ['us-east-1', 'us-west-2', 'eu-west-1'],
                    'implementation_groups': ['IG3'],
                    'engine_config': {
                        'max_workers': 12,
                        'memory_limit_mb': 2048
                    },
                    'mock_data': {
                        'ec2_instances': 500,
                        'iam_users': 300,
                        's3_buckets': 150,
                        'rds_instances': 50,
                        'lambda_functions': 100
                    }
                },
                {
                    'name': 'concurrent_assessments',
                    'description': 'Multiple concurrent assessments',
                    'regions': ['us-east-1'],
                    'implementation_groups': ['IG1'],
                    'engine_config': {
                        'max_workers': 16,
                        'memory_limit_mb': 1024
                    },
                    'concurrent_count': 3,
                    'mock_data': {
                        'ec2_instances': 100,
                        'iam_users': 50,
                        's3_buckets': 25
                    }
                }
            ],
            regression_threshold=1.3  # 30% performance degradation threshold
        )
    
    def generate_performance_report(self, results: Dict[str, List[BenchmarkResult]]) -> str:
        """Generate a performance report from benchmark results.
        
        Args:
            results: Benchmark results
            
        Returns:
            Performance report as string
        """
        report_lines = []
        report_lines.append("# Performance Benchmark Report")
        report_lines.append(f"Generated: {datetime.now().isoformat()}")
        report_lines.append("")
        
        for test_name, test_results in results.items():
            successful_results = [r for r in test_results if r.error_count == 0]
            
            if not successful_results:
                report_lines.append(f"## {test_name} - FAILED")
                report_lines.append("All iterations failed")
                report_lines.append("")
                continue
            
            # Calculate statistics
            execution_times = [r.execution_time_seconds for r in successful_results]
            memory_usage = [r.peak_memory_mb for r in successful_results]
            resource_counts = [r.total_resources_evaluated for r in successful_results]
            
            avg_time = statistics.mean(execution_times)
            min_time = min(execution_times)
            max_time = max(execution_times)
            
            avg_memory = statistics.mean(memory_usage)
            max_memory = max(memory_usage)
            
            avg_resources = statistics.mean(resource_counts)
            
            report_lines.append(f"## {test_name}")
            report_lines.append(f"- Successful runs: {len(successful_results)}/{len(test_results)}")
            report_lines.append(f"- Execution time: {avg_time:.2f}s (min: {min_time:.2f}s, max: {max_time:.2f}s)")
            report_lines.append(f"- Memory usage: {avg_memory:.1f}MB (peak: {max_memory:.1f}MB)")
            report_lines.append(f"- Resources evaluated: {avg_resources:.0f}")
            
            if successful_results[0].resource_stats:
                stats = successful_results[0].resource_stats
                report_lines.append(f"- API calls: {stats.total_api_calls} (failed: {stats.failed_api_calls})")
                report_lines.append(f"- Avg response time: {stats.avg_response_time_ms:.1f}ms")
            
            report_lines.append("")
        
        return "\n".join(report_lines)