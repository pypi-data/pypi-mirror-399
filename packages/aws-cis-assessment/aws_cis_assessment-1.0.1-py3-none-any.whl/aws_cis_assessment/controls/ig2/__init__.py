"""IG2 Enhanced Security Controls."""

from .control_3_10 import (
    APIGatewaySSLEnabledAssessment,
    ALBHTTPToHTTPSRedirectionAssessment,
    ELBTLSHTTPSListenersOnlyAssessment,
    S3BucketSSLRequestsOnlyAssessment,
    RedshiftRequireTLSSSLAssessment
)
from .control_3_11 import (
    EncryptedVolumesAssessment,
    RDSStorageEncryptedAssessment,
    S3DefaultEncryptionKMSAssessment,
    DynamoDBTableEncryptedKMSAssessment,
    BackupRecoveryPointEncryptedAssessment,
    EFSEncryptedCheckAssessment,
    SecretsManagerUsingKMSKeyAssessment,
    SNSTopicEncryptedKMSAssessment,
    SQSQueueEncryptedKMSAssessment,
    CloudWatchLogsEncryptedAssessment,
    KinesisStreamEncryptedAssessment,
    ElasticSearchDomainEncryptedAssessment
)
from .control_5_2 import (
    MFAEnabledForIAMConsoleAccessAssessment,
    RootAccountMFAEnabledAssessment,
    IAMUserUnusedCredentialsAssessment
)

__all__ = [
    # Control 3.10 - Encrypt Sensitive Data in Transit
    'APIGatewaySSLEnabledAssessment',
    'ALBHTTPToHTTPSRedirectionAssessment',
    'ELBTLSHTTPSListenersOnlyAssessment',
    'S3BucketSSLRequestsOnlyAssessment',
    'RedshiftRequireTLSSSLAssessment',
    
    # Control 3.11 - Encrypt Sensitive Data at Rest
    'EncryptedVolumesAssessment',
    'RDSStorageEncryptedAssessment',
    'S3DefaultEncryptionKMSAssessment',
    'DynamoDBTableEncryptedKMSAssessment',
    'BackupRecoveryPointEncryptedAssessment',
    'EFSEncryptedCheckAssessment',
    'SecretsManagerUsingKMSKeyAssessment',
    'SNSTopicEncryptedKMSAssessment',
    'SQSQueueEncryptedKMSAssessment',
    'CloudWatchLogsEncryptedAssessment',
    'KinesisStreamEncryptedAssessment',
    'ElasticSearchDomainEncryptedAssessment',
    
    # Control 5.2 - Use Unique Passwords
    'MFAEnabledForIAMConsoleAccessAssessment',
    'RootAccountMFAEnabledAssessment',
    'IAMUserUnusedCredentialsAssessment'
]