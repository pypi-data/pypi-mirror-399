"""Assessment Engine for orchestrating CIS Controls compliance assessments."""

import logging
import time
import gc
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
import weakref
import resource
import sys

from aws_cis_assessment.core.models import (
    AssessmentResult, ControlScore, IGScore, ComplianceResult, 
    ComplianceStatus, ImplementationGroup, CISControl
)
from aws_cis_assessment.core.aws_client_factory import AWSClientFactory
from aws_cis_assessment.core.scoring_engine import ScoringEngine
from aws_cis_assessment.config.config_loader import ConfigRuleLoader
from aws_cis_assessment.controls.base_control import BaseConfigRuleAssessment
from aws_cis_assessment.core.error_handler import ErrorHandler, ErrorContext, ErrorCategory
from aws_cis_assessment.core.audit_trail import AuditTrail, AuditEventType

# Import all control assessments
from aws_cis_assessment.controls.ig1.control_1_1 import (
    EIPAttachedAssessment, EC2StoppedInstanceAssessment, VPCNetworkACLUnusedAssessment,
    EC2InstanceManagedBySSMAssessment, EC2SecurityGroupAttachedAssessment
)
from aws_cis_assessment.controls.ig1.control_3_3 import (
    IAMPasswordPolicyAssessment, IAMUserMFAEnabledAssessment, IAMRootAccessKeyAssessment,
    S3BucketPublicReadProhibitedAssessment, EC2InstanceNoPublicIPAssessment
)
from aws_cis_assessment.controls.ig1.control_4_1 import (
    AccountPartOfOrganizationsAssessment, EC2VolumeInUseAssessment,
    RedshiftClusterMaintenanceSettingsAssessment, SecretsManagerRotationEnabledAssessment
)
from aws_cis_assessment.controls.ig2.control_3_10 import (
    APIGatewaySSLEnabledAssessment, ALBHTTPToHTTPSRedirectionAssessment,
    ELBTLSHTTPSListenersOnlyAssessment, S3BucketSSLRequestsOnlyAssessment,
    RedshiftRequireTLSSSLAssessment
)
from aws_cis_assessment.controls.ig2.control_3_11 import (
    EncryptedVolumesAssessment, RDSStorageEncryptedAssessment,
    S3DefaultEncryptionKMSAssessment, DynamoDBTableEncryptedKMSAssessment,
    BackupRecoveryPointEncryptedAssessment
)
from aws_cis_assessment.controls.ig2.control_5_2 import (
    MFAEnabledForIAMConsoleAccessAssessment, RootAccountMFAEnabledAssessment,
    IAMUserUnusedCredentialsAssessment
)
from aws_cis_assessment.controls.ig3.control_3_14 import (
    APIGatewayExecutionLoggingEnabledAssessment, CloudTrailS3DataEventsEnabledAssessment,
    MultiRegionCloudTrailEnabledAssessment, CloudTrailCloudWatchLogsEnabledAssessment
)
from aws_cis_assessment.controls.ig3.control_7_1 import (
    ECRPrivateImageScanningEnabledAssessment, GuardDutyEnabledCentralizedAssessment,
    EC2ManagedInstancePatchComplianceAssessment
)
from aws_cis_assessment.controls.ig3.control_12_8 import (
    APIGatewayAssociatedWithWAFAssessment, VPCSecurityGroupOpenOnlyToAuthorizedPortsAssessment,
    NoUnrestrictedRouteToIGWAssessment
)
from aws_cis_assessment.controls.ig3.control_13_1 import (
    RestrictedIncomingTrafficAssessment, IncomingSSHDisabledAssessment,
    VPCFlowLogsEnabledAssessment
)

logger = logging.getLogger(__name__)


@dataclass
class AssessmentProgress:
    """Progress tracking for assessment execution."""
    total_controls: int = 0
    completed_controls: int = 0
    total_regions: int = 0
    completed_regions: int = 0
    current_control: str = ""
    current_region: str = ""
    start_time: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None
    errors: List[str] = None
    memory_usage_mb: float = 0.0
    peak_memory_mb: float = 0.0
    active_threads: int = 0
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
    
    @property
    def progress_percentage(self) -> float:
        """Calculate overall progress percentage."""
        if self.total_controls == 0:
            return 0.0
        return (self.completed_controls / self.total_controls) * 100
    
    @property
    def elapsed_time(self) -> Optional[timedelta]:
        """Calculate elapsed time since start."""
        if self.start_time is None:
            return None
        return datetime.now() - self.start_time


@dataclass
class ResourceUsageStats:
    """Resource usage statistics for performance monitoring."""
    peak_memory_mb: float = 0.0
    current_memory_mb: float = 0.0
    cpu_time_seconds: float = 0.0
    active_connections: int = 0
    total_api_calls: int = 0
    failed_api_calls: int = 0
    avg_response_time_ms: float = 0.0
    
    def update_memory_usage(self):
        """Update current memory usage."""
        try:
            # Try to get memory usage from resource module (Unix-like systems)
            memory_kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            if sys.platform == 'darwin':  # macOS reports in bytes
                self.current_memory_mb = memory_kb / 1024 / 1024
            else:  # Linux reports in KB
                self.current_memory_mb = memory_kb / 1024
            
            if self.current_memory_mb > self.peak_memory_mb:
                self.peak_memory_mb = self.current_memory_mb
        except:
            # Fallback - try psutil if available
            try:
                import psutil
                process = psutil.Process()
                memory_info = process.memory_info()
                self.current_memory_mb = memory_info.rss / 1024 / 1024
                if self.current_memory_mb > self.peak_memory_mb:
                    self.peak_memory_mb = self.current_memory_mb
            except ImportError:
                pass


class AssessmentEngine:
    """Orchestrates the entire compliance assessment process."""
    
    def __init__(self, aws_credentials: Optional[Dict[str, str]] = None, 
                 regions: Optional[List[str]] = None, 
                 config_path: Optional[str] = None,
                 max_workers: int = 4,
                 progress_callback: Optional[Callable[[AssessmentProgress], None]] = None,
                 enable_error_recovery: bool = True,
                 enable_audit_trail: bool = True,
                 timeout: int = 3600,
                 memory_limit_mb: Optional[int] = None,
                 enable_resource_monitoring: bool = True):
        """Initialize assessment engine with AWS credentials and configuration.
        
        Args:
            aws_credentials: Optional AWS credentials dict
            regions: List of AWS regions to assess. If None, uses default regions.
            config_path: Path to CIS Controls configuration files
            max_workers: Maximum number of parallel workers for assessment
            progress_callback: Optional callback function for progress updates
            enable_error_recovery: Whether to enable error recovery mechanisms
            enable_audit_trail: Whether to enable audit trail logging
            timeout: Assessment timeout in seconds (default: 3600)
            memory_limit_mb: Optional memory limit in MB for resource management
            enable_resource_monitoring: Whether to enable resource usage monitoring
        """
        self.aws_factory = AWSClientFactory(aws_credentials, regions)
        self.config_loader = ConfigRuleLoader(config_path)
        self.scoring_engine = ScoringEngine()
        self.max_workers = max_workers
        self.timeout = timeout
        self.memory_limit_mb = memory_limit_mb
        self.enable_resource_monitoring = enable_resource_monitoring
        self.progress_callback = progress_callback
        self.progress = AssessmentProgress()
        self.resource_stats = ResourceUsageStats()
        self._progress_lock = threading.Lock()
        self._resource_lock = threading.Lock()
        self._client_cache = weakref.WeakValueDictionary()  # Weak references for memory management
        
        # Initialize error handling and audit trail
        self.error_handler = ErrorHandler() if enable_error_recovery else None
        self.audit_trail = AuditTrail() if enable_audit_trail else None
        
        # Initialize control assessment registry
        self._assessment_registry = self._build_assessment_registry()
        
        # Start resource monitoring thread if enabled
        self._monitoring_active = False
        self._monitoring_thread = None
        if self.enable_resource_monitoring:
            self._start_resource_monitoring()
        
        logger.info(f"Assessment Engine initialized for regions: {self.aws_factory.regions}")
        logger.info(f"Performance settings: max_workers={max_workers}, memory_limit={memory_limit_mb}MB")
        
        if self.audit_trail:
            self.audit_trail.log_event(
                event_type=AuditEventType.CONFIGURATION_LOAD,
                message="Assessment Engine initialized",
                details={
                    "regions": self.aws_factory.regions,
                    "max_workers": max_workers,
                    "memory_limit_mb": memory_limit_mb,
                    "resource_monitoring": enable_resource_monitoring,
                    "error_recovery_enabled": enable_error_recovery,
                    "audit_trail_enabled": enable_audit_trail
                }
            )
    
    def _build_assessment_registry(self) -> Dict[str, Dict[str, BaseConfigRuleAssessment]]:
        """Build registry of all available control assessments."""
        registry = {
            'IG1': {
                # Control 1.1 - Asset Inventory
                'eip-attached': EIPAttachedAssessment(),
                'ec2-stopped-instance': EC2StoppedInstanceAssessment(),
                'vpc-network-acl-unused-check': VPCNetworkACLUnusedAssessment(),
                'ec2-instance-managed-by-systems-manager': EC2InstanceManagedBySSMAssessment(),
                'ec2-security-group-attached-to-eni': EC2SecurityGroupAttachedAssessment(),
                
                # Control 3.3 - Data Access Control
                'iam-password-policy': IAMPasswordPolicyAssessment(),
                'iam-user-mfa-enabled': IAMUserMFAEnabledAssessment(),
                'iam-root-access-key-check': IAMRootAccessKeyAssessment(),
                's3-bucket-public-read-prohibited': S3BucketPublicReadProhibitedAssessment(),
                'ec2-instance-no-public-ip': EC2InstanceNoPublicIPAssessment(),
                
                # Control 4.1 - Secure Configuration
                'account-part-of-organizations': AccountPartOfOrganizationsAssessment(),
                'ec2-volume-inuse-check': EC2VolumeInUseAssessment(),
                'redshift-cluster-maintenancesettings-check': RedshiftClusterMaintenanceSettingsAssessment(),
                'secretsmanager-rotation-enabled-check': SecretsManagerRotationEnabledAssessment(),
            },
            'IG2': {
                # Control 3.10 - Encryption in Transit
                'api-gw-ssl-enabled': APIGatewaySSLEnabledAssessment(),
                'alb-http-to-https-redirection-check': ALBHTTPToHTTPSRedirectionAssessment(),
                'elb-tls-https-listeners-only': ELBTLSHTTPSListenersOnlyAssessment(),
                's3-bucket-ssl-requests-only': S3BucketSSLRequestsOnlyAssessment(),
                'redshift-require-tls-ssl': RedshiftRequireTLSSSLAssessment(),
                
                # Control 3.11 - Encryption at Rest
                'encrypted-volumes': EncryptedVolumesAssessment(),
                'rds-storage-encrypted': RDSStorageEncryptedAssessment(),
                's3-default-encryption-kms': S3DefaultEncryptionKMSAssessment(),
                'dynamodb-table-encrypted-kms': DynamoDBTableEncryptedKMSAssessment(),
                'backup-recovery-point-encrypted': BackupRecoveryPointEncryptedAssessment(),
                
                # Control 5.2 - Password Management
                'mfa-enabled-for-iam-console-access': MFAEnabledForIAMConsoleAccessAssessment(),
                'root-account-mfa-enabled': RootAccountMFAEnabledAssessment(),
                'iam-user-unused-credentials-check': IAMUserUnusedCredentialsAssessment(),
            },
            'IG3': {
                # Control 3.14 - Sensitive Data Logging
                'api-gw-execution-logging-enabled': APIGatewayExecutionLoggingEnabledAssessment(),
                'cloudtrail-s3-dataevents-enabled': CloudTrailS3DataEventsEnabledAssessment(),
                'multi-region-cloudtrail-enabled': MultiRegionCloudTrailEnabledAssessment(),
                'cloud-trail-cloud-watch-logs-enabled': CloudTrailCloudWatchLogsEnabledAssessment(),
                
                # Control 7.1 - Vulnerability Management
                'ecr-private-image-scanning-enabled': ECRPrivateImageScanningEnabledAssessment(),
                'guardduty-enabled-centralized': GuardDutyEnabledCentralizedAssessment(),
                'ec2-managedinstance-patch-compliance-status-check': EC2ManagedInstancePatchComplianceAssessment(),
                
                # Control 12.8 - Network Segmentation
                'api-gw-associated-with-waf': APIGatewayAssociatedWithWAFAssessment(),
                'vpc-sg-open-only-to-authorized-ports': VPCSecurityGroupOpenOnlyToAuthorizedPortsAssessment(),
                'no-unrestricted-route-to-igw': NoUnrestrictedRouteToIGWAssessment(),
                
                # Control 13.1 - Network Monitoring
                'restricted-incoming-traffic': RestrictedIncomingTrafficAssessment(),
                'incoming-ssh-disabled': IncomingSSHDisabledAssessment(),
                'vpc-flow-logs-enabled': VPCFlowLogsEnabledAssessment(),
            }
        }
        
        # Add IG1 assessments to IG2 and IG3 (inheritance)
        registry['IG2'].update(registry['IG1'])
        registry['IG3'].update(registry['IG2'])
        
        return registry
    
    def _start_resource_monitoring(self):
        """Start background resource monitoring thread."""
        self._monitoring_active = True
        self._monitoring_thread = threading.Thread(target=self._monitor_resources, daemon=True)
        self._monitoring_thread.start()
        logger.debug("Resource monitoring thread started")
    
    def _stop_resource_monitoring(self):
        """Stop background resource monitoring thread."""
        self._monitoring_active = False
        if self._monitoring_thread and self._monitoring_thread.is_alive():
            self._monitoring_thread.join(timeout=1.0)
        logger.debug("Resource monitoring thread stopped")
    
    def _monitor_resources(self):
        """Background thread to monitor resource usage."""
        while self._monitoring_active:
            try:
                with self._resource_lock:
                    self.resource_stats.update_memory_usage()
                    
                    # Update progress with current memory usage
                    with self._progress_lock:
                        self.progress.memory_usage_mb = self.resource_stats.current_memory_mb
                        self.progress.peak_memory_mb = self.resource_stats.peak_memory_mb
                    
                    # Check memory limit if set
                    if (self.memory_limit_mb and 
                        self.resource_stats.current_memory_mb > self.memory_limit_mb):
                        logger.warning(f"Memory usage ({self.resource_stats.current_memory_mb:.1f}MB) "
                                     f"exceeds limit ({self.memory_limit_mb}MB). Triggering garbage collection.")
                        self._optimize_memory_usage()
                
                time.sleep(1.0)  # Monitor every second
            except Exception as e:
                logger.debug(f"Resource monitoring error: {e}")
                time.sleep(5.0)  # Back off on errors
    
    def _optimize_memory_usage(self):
        """Optimize memory usage by cleaning up resources."""
        try:
            # Force garbage collection
            collected = gc.collect()
            logger.debug(f"Garbage collection freed {collected} objects")
            
            # Clear weak reference cache
            self._client_cache.clear()
            
            # Clear any cached data in AWS factory
            if hasattr(self.aws_factory, '_clients'):
                # Keep only essential clients, clear others
                essential_services = ['sts', 'ec2', 'iam']
                clients_to_remove = []
                for key in self.aws_factory._clients.keys():
                    service_name = key.split('_')[0]
                    if service_name not in essential_services:
                        clients_to_remove.append(key)
                
                for key in clients_to_remove:
                    self.aws_factory._clients.pop(key, None)
                
                logger.debug(f"Cleared {len(clients_to_remove)} cached AWS clients")
            
            # Update memory stats after cleanup
            self.resource_stats.update_memory_usage()
            
        except Exception as e:
            logger.warning(f"Memory optimization failed: {e}")
    
    def get_resource_stats(self) -> ResourceUsageStats:
        """Get current resource usage statistics.
        
        Returns:
            ResourceUsageStats object with current metrics
        """
        with self._resource_lock:
            self.resource_stats.update_memory_usage()
            return ResourceUsageStats(
                peak_memory_mb=self.resource_stats.peak_memory_mb,
                current_memory_mb=self.resource_stats.current_memory_mb,
                cpu_time_seconds=self.resource_stats.cpu_time_seconds,
                active_connections=self.resource_stats.active_connections,
                total_api_calls=self.resource_stats.total_api_calls,
                failed_api_calls=self.resource_stats.failed_api_calls,
                avg_response_time_ms=self.resource_stats.avg_response_time_ms
            )
    
    def run_assessment(self, implementation_groups: Optional[List[str]] = None,
                      controls: Optional[List[str]] = None,
                      exclude_controls: Optional[List[str]] = None) -> AssessmentResult:
        """Execute compliance assessment for specified Implementation Groups.
        
        Args:
            implementation_groups: List of IGs to assess (IG1, IG2, IG3). If None, assesses all.
            controls: List of specific control IDs to assess. If specified, overrides implementation_groups.
            exclude_controls: List of control IDs to exclude from assessment.
            
        Returns:
            AssessmentResult with complete assessment data
        """
        if implementation_groups is None:
            implementation_groups = ['IG1', 'IG2', 'IG3']
        
        # Validate implementation groups
        valid_igs = [ig.value for ig in ImplementationGroup]
        for ig in implementation_groups:
            if ig not in valid_igs:
                raise ValueError(f"Invalid implementation group: {ig}. Valid options: {valid_igs}")
        
        logger.info(f"Starting assessment for Implementation Groups: {implementation_groups}")
        if controls:
            logger.info(f"Specific controls requested: {controls}")
        if exclude_controls:
            logger.info(f"Excluded controls: {exclude_controls}")
        
        # Log assessment start
        if self.audit_trail:
            account_info = self.aws_factory.get_account_info()
            account_id = account_info.get('account_id', 'unknown')
            self.audit_trail.log_assessment_start(
                account_id=account_id,
                regions=self.aws_factory.regions,
                implementation_groups=implementation_groups
            )
        
        # Initialize progress tracking
        with self._progress_lock:
            self.progress = AssessmentProgress(
                start_time=datetime.now(),
                total_regions=len(self.aws_factory.regions)
            )
            
            # Count total controls to assess
            total_controls = 0
            for ig in implementation_groups:
                if ig in self._assessment_registry:
                    ig_controls = self._filter_controls_for_ig(ig, controls, exclude_controls)
                    total_controls += len(ig_controls)
            self.progress.total_controls = total_controls
        
        self._update_progress()
        
        try:
            # Validate AWS credentials with error handling
            credential_validation_start = time.time()
            
            def validate_credentials():
                return self.aws_factory.validate_credentials()
            
            if self.error_handler:
                context = ErrorContext(operation="credential_validation")
                validation_result = self.error_handler.handle_error(
                    Exception("Credential validation"), context, validate_credentials
                )
                if validation_result is None:
                    if not self.aws_factory.validate_credentials():
                        raise RuntimeError("AWS credential validation failed")
            else:
                if not self.aws_factory.validate_credentials():
                    raise RuntimeError("AWS credential validation failed")
            
            # Log credential validation
            if self.audit_trail:
                validation_duration = int((time.time() - credential_validation_start) * 1000)
                self.audit_trail.log_event(
                    event_type=AuditEventType.CREDENTIAL_VALIDATION,
                    status="SUCCESS",
                    message="AWS credentials validated successfully",
                    duration_ms=validation_duration
                )
            
            account_info = self.aws_factory.get_account_info()
            account_id = account_info.get('account_id', 'unknown')
            
            # Execute assessments for each Implementation Group
            ig_scores = {}
            all_results = []
            
            for ig in implementation_groups:
                logger.info(f"Assessing Implementation Group: {ig}")
                
                ig_results = self._assess_implementation_group(ig, controls, exclude_controls)
                all_results.extend(ig_results)
                
                # Calculate IG score using scoring engine
                ig_score = self._calculate_ig_score(ig, ig_results)
                ig_scores[ig] = ig_score
                
                logger.info(f"Completed {ig} assessment: {ig_score.compliance_percentage:.1f}% compliant")
            
            # Calculate overall score using scoring engine
            overall_score = self.scoring_engine.calculate_overall_score(ig_scores)
            
            # Create final assessment result
            assessment_result = AssessmentResult(
                account_id=account_id,
                regions_assessed=self.aws_factory.regions.copy(),
                timestamp=datetime.now(),
                overall_score=overall_score,
                ig_scores=ig_scores,
                total_resources_evaluated=len(all_results),
                assessment_duration=self.progress.elapsed_time
            )
            
            # Log assessment completion
            if self.audit_trail:
                self.audit_trail.log_assessment_complete(
                    account_id=account_id,
                    overall_score=overall_score,
                    total_resources=len(all_results),
                    duration=self.progress.elapsed_time or timedelta(0)
                )
            
            logger.info(f"Assessment completed. Overall compliance: {overall_score:.1f}%")
            logger.info(f"Resource usage: Peak memory {self.resource_stats.peak_memory_mb:.1f}MB")
            
            return assessment_result
            
        except Exception as e:
            logger.error(f"Assessment failed: {e}")
            
            # Log assessment error
            if self.audit_trail:
                self.audit_trail.log_event(
                    event_type=AuditEventType.ASSESSMENT_ERROR,
                    status="FAILURE",
                    message=f"Assessment failed: {str(e)}",
                    details={"exception_type": type(e).__name__}
                )
            
            # Handle error with error handler
            if self.error_handler:
                context = ErrorContext(operation="assessment_execution")
                self.error_handler.handle_error(e, context)
            
            with self._progress_lock:
                self.progress.errors.append(f"Assessment failed: {str(e)}")
            self._update_progress()
            raise
        
        finally:
            # Cleanup resources
            self._cleanup_resources()
    
    def _assess_implementation_group(self, implementation_group: str,
                                    controls: Optional[List[str]] = None,
                                    exclude_controls: Optional[List[str]] = None) -> List[ComplianceResult]:
        """Assess all controls for a specific Implementation Group.
        
        Args:
            implementation_group: IG1, IG2, or IG3
            controls: List of specific control IDs to assess
            exclude_controls: List of control IDs to exclude
            
        Returns:
            List of ComplianceResult objects
        """
        if implementation_group not in self._assessment_registry:
            logger.warning(f"No assessments found for Implementation Group: {implementation_group}")
            return []
        
        # Filter assessments based on criteria
        assessments = self._filter_controls_for_ig(implementation_group, controls, exclude_controls)
        all_results = []
        
        # Calculate optimal batch size based on memory constraints
        batch_size = self._calculate_optimal_batch_size(len(assessments))
        assessment_items = list(assessments.items())
        
        # Process assessments in batches to manage memory usage
        for batch_start in range(0, len(assessment_items), batch_size):
            batch_end = min(batch_start + batch_size, len(assessment_items))
            batch_assessments = dict(assessment_items[batch_start:batch_end])
            
            logger.debug(f"Processing batch {batch_start//batch_size + 1}: "
                        f"{len(batch_assessments)} assessments")
            
            # Use ThreadPoolExecutor for parallel assessment execution within batch
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit assessment tasks for current batch
                future_to_assessment = {}
                
                for rule_name, assessment in batch_assessments.items():
                    for region in self.aws_factory.regions:
                        future = executor.submit(
                            self._run_single_assessment, assessment, region, rule_name
                        )
                        future_to_assessment[future] = (rule_name, region)
                        
                        # Update active threads count
                        with self._progress_lock:
                            self.progress.active_threads = len(future_to_assessment)
                
                # Collect results as they complete
                batch_results = []
                for future in as_completed(future_to_assessment):
                    rule_name, region = future_to_assessment[future]
                    
                    try:
                        results = future.result()
                        batch_results.extend(results)
                        
                        with self._progress_lock:
                            self.progress.completed_controls += 1
                            self.progress.current_control = rule_name
                            self.progress.current_region = region
                            self.progress.active_threads = len([f for f in future_to_assessment if not f.done()])
                        
                        self._update_progress()
                        
                        logger.debug(f"Completed assessment: {rule_name} in {region} ({len(results)} results)")
                        
                    except Exception as e:
                        error_msg = f"Assessment failed for {rule_name} in {region}: {str(e)}"
                        logger.error(error_msg)
                        
                        with self._progress_lock:
                            self.progress.errors.append(error_msg)
                            self.progress.completed_controls += 1
                        
                        self._update_progress()
            
            # Add batch results to overall results
            all_results.extend(batch_results)
            
            # Optimize memory usage between batches
            if batch_end < len(assessment_items):
                self._optimize_memory_usage()
                logger.debug(f"Completed batch {batch_start//batch_size + 1}, "
                           f"memory usage: {self.resource_stats.current_memory_mb:.1f}MB")
        
        return all_results
    
    def _calculate_optimal_batch_size(self, total_assessments: int) -> int:
        """Calculate optimal batch size based on available resources.
        
        Args:
            total_assessments: Total number of assessments to process
            
        Returns:
            Optimal batch size for memory management
        """
        # Base batch size on memory constraints and worker count
        base_batch_size = max(self.max_workers * 2, 10)  # At least 2x workers, minimum 10
        
        if self.memory_limit_mb:
            # Estimate memory per assessment (rough heuristic)
            estimated_memory_per_assessment = 5  # MB
            max_assessments_for_memory = self.memory_limit_mb // estimated_memory_per_assessment
            base_batch_size = min(base_batch_size, max_assessments_for_memory)
        
        # Don't exceed total assessments
        return min(base_batch_size, total_assessments)
    
    def _run_single_assessment(self, assessment: BaseConfigRuleAssessment, 
                             region: str, rule_name: str) -> List[ComplianceResult]:
        """Run a single assessment in a specific region with error handling.
        
        Args:
            assessment: Assessment instance to run
            region: AWS region
            rule_name: Name of the Config rule
            
        Returns:
            List of ComplianceResult objects
        """
        assessment_start_time = time.time()
        
        try:
            logger.debug(f"Starting assessment: {rule_name} in region {region}")
            
            # Check service availability if error handler is enabled
            if self.error_handler:
                required_services = assessment._get_required_services()
                for service in required_services:
                    if not self.error_handler.is_service_available(service, region):
                        logger.warning(f"Service {service} marked as unavailable in {region}, skipping {rule_name}")
                        return [ComplianceResult(
                            resource_id=f"SKIPPED_{rule_name}_{region}",
                            resource_type="SKIPPED",
                            compliance_status=ComplianceStatus.NOT_APPLICABLE,
                            evaluation_reason=f"Service {service} unavailable in region {region}",
                            config_rule_name=rule_name,
                            region=region
                        )]
            
            # Execute assessment with error handling
            def run_assessment():
                return assessment.evaluate_compliance(self.aws_factory, region)
            
            if self.error_handler:
                context = ErrorContext(
                    service_name=assessment._get_required_services()[0] if assessment._get_required_services() else "",
                    region=region,
                    operation="evaluate_compliance",
                    control_id=assessment.control_id,
                    config_rule_name=rule_name
                )
                
                results = self.error_handler.handle_error(
                    Exception("Assessment execution"), context, run_assessment
                )
                
                if results is None:
                    results = run_assessment()
            else:
                results = run_assessment()
            
            assessment_duration = int((time.time() - assessment_start_time) * 1000)
            
            # Log control evaluation
            if self.audit_trail:
                compliant_count = sum(1 for r in results if r.compliance_status == ComplianceStatus.COMPLIANT)
                self.audit_trail.log_control_evaluation(
                    control_id=assessment.control_id,
                    config_rule_name=rule_name,
                    region=region,
                    resource_count=len(results),
                    compliant_count=compliant_count,
                    duration_ms=assessment_duration
                )
            
            logger.debug(f"Assessment {rule_name} in {region} completed with {len(results)} results")
            return results
            
        except Exception as e:
            assessment_duration = int((time.time() - assessment_start_time) * 1000)
            
            logger.error(f"Error in assessment {rule_name} for region {region}: {e}")
            
            # Log assessment error
            if self.audit_trail:
                self.audit_trail.log_event(
                    event_type=AuditEventType.ASSESSMENT_ERROR,
                    region=region,
                    service_name=assessment._get_required_services()[0] if assessment._get_required_services() else "",
                    operation=rule_name,
                    status="FAILURE",
                    message=f"Assessment error: {str(e)}",
                    duration_ms=assessment_duration,
                    details={
                        "control_id": assessment.control_id,
                        "exception_type": type(e).__name__
                    }
                )
            
            # Handle error with error handler
            if self.error_handler:
                context = ErrorContext(
                    service_name=assessment._get_required_services()[0] if assessment._get_required_services() else "",
                    region=region,
                    operation=rule_name,
                    control_id=assessment.control_id,
                    config_rule_name=rule_name
                )
                self.error_handler.handle_error(e, context)
            
            # Return error result instead of failing completely
            return [ComplianceResult(
                resource_id=f"ERROR_{rule_name}_{region}",
                resource_type="ERROR",
                compliance_status=ComplianceStatus.ERROR,
                evaluation_reason=f"Assessment error: {str(e)}",
                config_rule_name=rule_name,
                region=region
            )]
    
    def _calculate_ig_score(self, implementation_group: str, 
                           results: List[ComplianceResult]) -> IGScore:
        """Calculate compliance score for an Implementation Group using ScoringEngine.
        
        Args:
            implementation_group: IG1, IG2, or IG3
            results: List of compliance results
            
        Returns:
            IGScore object
        """
        # Group results by control ID
        results_by_control = {}
        for result in results:
            # Extract control ID from the assessment registry
            control_id = self._get_control_id_for_rule(result.config_rule_name, implementation_group)
            if control_id not in results_by_control:
                results_by_control[control_id] = []
            results_by_control[control_id].append(result)
        
        # Calculate control scores using scoring engine
        control_scores = {}
        for control_id, control_results in results_by_control.items():
            control_score = self.scoring_engine.calculate_control_score(
                control_id=control_id,
                rule_results=control_results,
                control_title=f"CIS Control {control_id}",
                implementation_group=implementation_group
            )
            control_scores[control_id] = control_score
        
        # Calculate IG score using scoring engine
        return self.scoring_engine.calculate_ig_score(implementation_group, control_scores)
    
    def _calculate_control_score(self, control_id: str, 
                               results: List[ComplianceResult]) -> ControlScore:
        """Calculate compliance score for a specific control using ScoringEngine.
        
        Args:
            control_id: CIS Control ID
            results: List of compliance results for the control
            
        Returns:
            ControlScore object
        """
        return self.scoring_engine.calculate_control_score(
            control_id=control_id,
            rule_results=results,
            control_title=f"CIS Control {control_id}"
        )
    
    def generate_compliance_summary(self, assessment_result: AssessmentResult):
        """Generate executive summary using ScoringEngine.
        
        Args:
            assessment_result: Complete assessment result
            
        Returns:
            ComplianceSummary object
        """
        return self.scoring_engine.generate_compliance_summary(assessment_result)
    
    def get_scoring_engine(self) -> ScoringEngine:
        """Get the scoring engine instance.
        
        Returns:
            ScoringEngine instance
        """
        return self.scoring_engine
    
    def _get_control_id_for_rule(self, rule_name: str, implementation_group: str) -> str:
        """Get control ID for a specific Config rule.
        
        Args:
            rule_name: AWS Config rule name
            implementation_group: Implementation Group
            
        Returns:
            Control ID string
        """
        if implementation_group in self._assessment_registry:
            assessment = self._assessment_registry[implementation_group].get(rule_name)
            if assessment:
                return assessment.control_id
        
        # Fallback - try to determine from rule name patterns
        if 'iam' in rule_name or 'password' in rule_name or 'mfa' in rule_name:
            return '3.3'  # Access Control
        elif 'eip' in rule_name or 'instance' in rule_name or 'volume' in rule_name:
            return '1.1'  # Asset Inventory
        elif 'ssl' in rule_name or 'tls' in rule_name or 'encrypt' in rule_name:
            return '3.10'  # Encryption
        elif 'log' in rule_name or 'trail' in rule_name:
            return '3.14'  # Logging
        else:
            return 'unknown'
    
    def _update_progress(self):
        """Update progress and call progress callback if provided."""
        if self.progress_callback:
            try:
                self.progress_callback(self.progress)
            except Exception as e:
                logger.warning(f"Progress callback failed: {e}")
    
    def get_supported_controls(self) -> Dict[str, List[str]]:
        """Return mapping of Implementation Groups to supported CIS Controls.
        
        Returns:
            Dictionary mapping IG names to lists of control IDs
        """
        supported_controls = {}
        
        for ig, assessments in self._assessment_registry.items():
            control_ids = set()
            for assessment in assessments.values():
                control_ids.add(assessment.control_id)
            supported_controls[ig] = sorted(list(control_ids))
        
        return supported_controls
    
    def validate_configuration(self) -> List[str]:
        """Validate assessment configuration and return any errors.
        
        Returns:
            List of validation error messages
        """
        errors = []
        
        # Validate config loader
        try:
            config_errors = self.config_loader.validate_configuration()
            errors.extend(config_errors)
        except Exception as e:
            errors.append(f"Config loader validation failed: {str(e)}")
        
        # Validate AWS credentials
        try:
            if not self.aws_factory.validate_credentials():
                errors.append("AWS credential validation failed")
        except Exception as e:
            errors.append(f"AWS credential validation error: {str(e)}")
        
        # Validate assessment registry
        if not self._assessment_registry:
            errors.append("No assessment implementations found")
        
        for ig, assessments in self._assessment_registry.items():
            if not assessments:
                errors.append(f"No assessments found for Implementation Group: {ig}")
        
        return errors
    
    def get_assessment_summary(self, implementation_groups: Optional[List[str]] = None,
                              controls: Optional[List[str]] = None,
                              exclude_controls: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get summary of available assessments.
        
        Args:
            implementation_groups: List of IGs to include in summary
            controls: List of specific control IDs to include
            exclude_controls: List of control IDs to exclude
        
        Returns:
            Dictionary with assessment summary information
        """
        if implementation_groups is None:
            implementation_groups = list(self._assessment_registry.keys())
        
        summary = {
            'implementation_groups': implementation_groups,
            'total_assessments': 0,
            'regions': self.aws_factory.regions.copy(),
            'supported_services': self.aws_factory.get_supported_services(),
            'assessments_by_ig': {}
        }
        
        total_assessments = 0
        for ig in implementation_groups:
            if ig in self._assessment_registry:
                ig_controls = self._filter_controls_for_ig(ig, controls, exclude_controls)
                summary['assessments_by_ig'][ig] = {
                    'count': len(ig_controls),
                    'rules': list(ig_controls.keys())
                }
                total_assessments += len(ig_controls)
        
        summary['total_assessments'] = total_assessments
        return summary
    
    def _filter_controls_for_ig(self, implementation_group: str, 
                               controls: Optional[List[str]] = None,
                               exclude_controls: Optional[List[str]] = None) -> Dict[str, BaseConfigRuleAssessment]:
        """Filter controls for an Implementation Group based on criteria.
        
        Args:
            implementation_group: IG to filter controls for
            controls: List of specific control IDs to include
            exclude_controls: List of control IDs to exclude
            
        Returns:
            Dictionary of filtered control assessments
        """
        if implementation_group not in self._assessment_registry:
            return {}
        
        all_assessments = self._assessment_registry[implementation_group]
        
        # If specific controls are requested, filter by control ID
        if controls:
            filtered_assessments = {}
            for rule_name, assessment in all_assessments.items():
                control_id = self._get_control_id_for_rule(rule_name, implementation_group)
                if control_id in controls:
                    filtered_assessments[rule_name] = assessment
            all_assessments = filtered_assessments
        
        # Exclude specified controls
        if exclude_controls:
            filtered_assessments = {}
            for rule_name, assessment in all_assessments.items():
                control_id = self._get_control_id_for_rule(rule_name, implementation_group)
                if control_id not in exclude_controls:
                    filtered_assessments[rule_name] = assessment
            all_assessments = filtered_assessments
        
        return all_assessments
    
    def get_error_summary(self) -> Optional[Dict[str, Any]]:
        """Get summary of errors encountered during assessment.
        
        Returns:
            Error summary dictionary or None if error handling disabled
        """
        if not self.error_handler:
            return None
        
        return self.error_handler.get_error_summary()
    
    def get_troubleshooting_report(self) -> Optional[List[Dict[str, Any]]]:
        """Get troubleshooting report for critical errors.
        
        Returns:
            List of troubleshooting information or None if error handling disabled
        """
        if not self.error_handler:
            return None
        
        return self.error_handler.get_troubleshooting_report()
    
    def get_audit_summary(self) -> Optional[Dict[str, Any]]:
        """Get audit trail summary for current session.
        
        Returns:
            Audit summary dictionary or None if audit trail disabled
        """
        if not self.audit_trail:
            return None
        
        return self.audit_trail.get_session_summary()
    
    def export_audit_trail(self, output_path: str, format: str = "json") -> bool:
        """Export audit trail to file.
        
        Args:
            output_path: Output file path
            format: Export format ("json" or "csv")
            
        Returns:
            True if export successful, False otherwise
        """
        if not self.audit_trail:
            logger.warning("Audit trail not enabled, cannot export")
            return False
        
        return self.audit_trail.export_session_events(output_path, format)
    
    def _cleanup_resources(self):
        """Clean up resources after assessment completion."""
        try:
            # Stop resource monitoring
            if self.enable_resource_monitoring:
                self._stop_resource_monitoring()
            
            # Clear client cache
            self._client_cache.clear()
            
            # Clean up AWS factory resources
            if hasattr(self.aws_factory, 'cleanup'):
                self.aws_factory.cleanup()
            
            # Force garbage collection
            gc.collect()
            
            logger.debug("Assessment resources cleaned up")
            
        except Exception as e:
            logger.warning(f"Resource cleanup failed: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with resource cleanup."""
        self._cleanup_resources()
        return False