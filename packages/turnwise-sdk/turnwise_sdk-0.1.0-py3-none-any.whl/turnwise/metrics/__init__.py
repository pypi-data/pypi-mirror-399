"""Pre-built evaluation metrics for common use cases.

These metrics match the system templates available in the TurnWise platform.
"""

from .default_metrics import (
    # Message Level Metrics
    ResponseQuality,
    GoalProgress,
    HallucinationDetection,
    ResponseCompleteness,
    ProfessionalTone,
    ReAskDetection,
    UserCorrectionDetection,
    SycophancyDetection,
    DeceptionDetection,
    SelfPreservationDetection,
    ManipulationDetection,
    InstructionOverrideAttempt,
    # Step Level Metrics
    ToolSelection,
    ParameterValidity,
    ToolResultHandling,
    ThinkingQuality,
    SelfCorrectionAwareness,
    StepCorrectness,
    ComprehensiveStepAnalysis,
    PowerSeekingBehavior,
    # Conversation Level Metrics
    ConversationFlow,
    TaskCompletion,
    Efficiency,
    TrajectoryQuality,
    UserSatisfactionPrediction,
    IntentDrift,
    ComprehensiveConversationAnalysis,
    RewardHackingDetection,
    ComprehensiveSafetyAnalysis,
    # Convenience collections
    MESSAGE_METRICS,
    STEP_METRICS,
    CONVERSATION_METRICS,
    SAFETY_METRICS,
    ALL_METRICS,
)

__all__ = [
    # Message Level
    "ResponseQuality",
    "GoalProgress",
    "HallucinationDetection",
    "ResponseCompleteness",
    "ProfessionalTone",
    "ReAskDetection",
    "UserCorrectionDetection",
    "SycophancyDetection",
    "DeceptionDetection",
    "SelfPreservationDetection",
    "ManipulationDetection",
    "InstructionOverrideAttempt",
    # Step Level
    "ToolSelection",
    "ParameterValidity",
    "ToolResultHandling",
    "ThinkingQuality",
    "SelfCorrectionAwareness",
    "StepCorrectness",
    "ComprehensiveStepAnalysis",
    "PowerSeekingBehavior",
    # Conversation Level
    "ConversationFlow",
    "TaskCompletion",
    "Efficiency",
    "TrajectoryQuality",
    "UserSatisfactionPrediction",
    "IntentDrift",
    "ComprehensiveConversationAnalysis",
    "RewardHackingDetection",
    "ComprehensiveSafetyAnalysis",
    # Collections
    "MESSAGE_METRICS",
    "STEP_METRICS",
    "CONVERSATION_METRICS",
    "SAFETY_METRICS",
    "ALL_METRICS",
]
