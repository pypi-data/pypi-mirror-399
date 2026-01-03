
import torch.optim as optim
from torch.optim.lr_scheduler import LinearLR, CosineAnnealingLR, SequentialLR, ConstantLR

def get_scheduler(optimizer, warmup_epochs, total_epochs, scheduler_type="warmup_cosine"):
    """
    Creates a learning rate scheduler with warm-up.
    
    Args:
        optimizer: The optimizer to schedule.
        warmup_epochs: Number of epochs for linear warm-up.
        total_epochs: Total number of training epochs.
        scheduler_type: Type of scheduler ("warmup_cosine", "warmup_constant", "none").
    
    Returns:
        A PyTorch LR scheduler or None.
    """
    if scheduler_type == "none" or not scheduler_type:
        return None
    
    # Handle case with no warmup
    if warmup_epochs <= 0:
        if scheduler_type == "warmup_cosine" or scheduler_type == "cosine":
            return CosineAnnealingLR(optimizer, T_max=total_epochs)
        else:
            return None

    # 1. Warm-up Phase: Linearly increase LR from small factor to 1.0
    # start_factor=0.01 implies starting at 1% of target LR
    scheduler1 = LinearLR(optimizer, start_factor=0.01, end_factor=1.0, total_iters=warmup_epochs)
    
    # 2. Main Phase
    remaining_epochs = max(1, total_epochs - warmup_epochs)
    
    if scheduler_type == "warmup_cosine":
        # Cosine decay for the remaining epochs
        scheduler2 = CosineAnnealingLR(optimizer, T_max=remaining_epochs)
    elif scheduler_type == "warmup_constant":
        # Constant LR for the remaining epochs
        scheduler2 = ConstantLR(optimizer, factor=1.0, total_iters=remaining_epochs)
    else:
        # If type is just "warmup", we can just return scheduler1 (though usually we want to maintain after)
        # But for safety, let's assume constant after warmup if unknown
        scheduler2 = ConstantLR(optimizer, factor=1.0, total_iters=remaining_epochs)

    # Combine using SequentialLR
    # milestones=[warmup_epochs] means transition happens after warmup_epochs
    scheduler = SequentialLR(optimizer, schedulers=[scheduler1, scheduler2], milestones=[warmup_epochs])
    return scheduler
