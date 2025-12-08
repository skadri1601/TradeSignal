"""
Tickets API Router
Endpoints for user support tickets.
"""

import logging
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from pydantic import BaseModel

from app.database import get_db
from app.models.user import User
from app.models.ticket import Ticket, TicketMessage, TicketStatus
from app.core.security import get_current_active_user, get_current_support_or_superuser

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tickets", tags=["Tickets"])


# Models
class TicketCreate(BaseModel):
    subject: str
    message: str
    priority: str = "medium"


class TicketMessageCreate(BaseModel):
    message: str


class TicketMessageResponse(BaseModel):
    id: int
    ticket_id: int
    user_id: int
    message: str
    is_staff_reply: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TicketResponse(BaseModel):
    id: int
    user_id: int
    subject: str
    status: str
    priority: str
    created_at: datetime
    updated_at: datetime
    messages: List[TicketMessageResponse] = []

    class Config:
        from_attributes = True


# User Endpoints


@router.post("/", response_model=TicketResponse)
async def create_ticket(
    ticket_data: TicketCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new support ticket."""
    try:
        # Validate priority
        valid_priorities = ["low", "medium", "high"]
        priority = ticket_data.priority.lower() if ticket_data.priority else "medium"
        if priority not in valid_priorities:
            priority = "medium"
        
    # Create ticket
    ticket = Ticket(
        user_id=current_user.id,
        subject=ticket_data.subject,
        status=TicketStatus.OPEN.value,
            priority=priority,
    )
    db.add(ticket)
    await db.flush()  # Get ID

    # Create initial message
    message = TicketMessage(
        ticket_id=ticket.id,
        user_id=current_user.id,
        message=ticket_data.message,
        is_staff_reply=False,
    )
    db.add(message)

    await db.commit()
        
        # Refresh ticket to get updated timestamps
    await db.refresh(ticket)

        # Explicitly load messages for the response
        msg_result = await db.execute(
            select(TicketMessage)
            .where(TicketMessage.ticket_id == ticket.id)
            .order_by(TicketMessage.created_at)
        )
        messages = msg_result.scalars().all()
        
        # Create response with messages
        ticket_response = TicketResponse(
            id=ticket.id,
            user_id=ticket.user_id,
            subject=ticket.subject,
            status=ticket.status,
            priority=ticket.priority,
            created_at=ticket.created_at,
            updated_at=ticket.updated_at,
            messages=[TicketMessageResponse.model_validate(m) for m in messages],
        )
        
        logger.info(
            f"Ticket created successfully: ID={ticket.id}, User ID={current_user.id}, Subject={ticket_data.subject[:50]}"
        )
        
        return ticket_response
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating ticket: {e}", exc_info=True)
        logger.error(f"  User ID: {current_user.id if current_user else 'None'}")
        logger.error(f"  Subject: {ticket_data.subject if ticket_data else 'None'}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while creating the ticket. Please try again later.",
        )


@router.get("/", response_model=List[TicketResponse])
async def list_my_tickets(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """List current user's tickets."""
    try:
    result = await db.execute(
        select(Ticket)
        .where(Ticket.user_id == current_user.id)
        .order_by(desc(Ticket.updated_at))
    )
        tickets = result.scalars().all()
        
        # Load messages for each ticket
        ticket_responses = []
        for ticket in tickets:
            msg_result = await db.execute(
                select(TicketMessage)
                .where(TicketMessage.ticket_id == ticket.id)
                .order_by(TicketMessage.created_at)
            )
            messages = msg_result.scalars().all()
            
            ticket_response = TicketResponse(
                id=ticket.id,
                user_id=ticket.user_id,
                subject=ticket.subject,
                status=ticket.status,
                priority=ticket.priority,
                created_at=ticket.created_at,
                updated_at=ticket.updated_at,
                messages=[TicketMessageResponse.model_validate(m) for m in messages],
            )
            ticket_responses.append(ticket_response)
        
        return ticket_responses
    except Exception as e:
        logger.error(f"Error listing tickets for user {current_user.id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while fetching tickets. Please try again later.",
        )


@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(
    ticket_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific ticket."""
    try:
    result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
    ticket = result.scalar_one_or_none()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if ticket.user_id != current_user.id and current_user.role not in [
        "support",
        "super_admin",
    ]:
        raise HTTPException(
            status_code=403, detail="Not authorized to view this ticket"
        )

    # Load messages
    msg_result = await db.execute(
        select(TicketMessage)
        .where(TicketMessage.ticket_id == ticket_id)
        .order_by(TicketMessage.created_at)
    )
        messages = msg_result.scalars().all()

        # Create proper response
        ticket_response = TicketResponse(
            id=ticket.id,
            user_id=ticket.user_id,
            subject=ticket.subject,
            status=ticket.status,
            priority=ticket.priority,
            created_at=ticket.created_at,
            updated_at=ticket.updated_at,
            messages=[TicketMessageResponse.model_validate(m) for m in messages],
        )

        return ticket_response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching ticket {ticket_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while fetching the ticket. Please try again later.",
        )


@router.post("/{ticket_id}/reply", response_model=TicketMessageResponse)
async def reply_ticket(
    ticket_id: int,
    reply_data: TicketMessageCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Reply to a ticket."""
    try:
    result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
    ticket = result.scalar_one_or_none()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    is_staff = current_user.role in ["support", "super_admin"]

    if not is_staff and ticket.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Create message
    message = TicketMessage(
        ticket_id=ticket_id,
        user_id=current_user.id,
        message=reply_data.message,
        is_staff_reply=is_staff,
    )
    db.add(message)

    # Update ticket status and timestamp
    ticket.updated_at = datetime.utcnow()
    if is_staff:
        ticket.status = TicketStatus.ANSWERED.value
    else:
        ticket.status = TicketStatus.OPEN.value  # Re-open if user replies

    await db.commit()
    await db.refresh(message)

        logger.info(
            f"Reply added to ticket {ticket_id} by user {current_user.id} (staff: {is_staff})"
        )

    return message
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error replying to ticket {ticket_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while adding the reply. Please try again later.",
        )


# Admin Endpoints


@router.get("/admin/all", response_model=List[TicketResponse])
async def list_all_tickets(
    ticket_status: Optional[str] = Query(None, alias="status"),
    current_user: User = Depends(get_current_support_or_superuser),
    db: AsyncSession = Depends(get_db),
):
    """List all tickets (for support staff)."""
    try:
    query = select(Ticket).order_by(desc(Ticket.updated_at))

    if ticket_status:
        query = query.where(Ticket.status == ticket_status)

    result = await db.execute(query)
        tickets = result.scalars().all()
        
        # Load messages for each ticket
        ticket_responses = []
        for ticket in tickets:
            msg_result = await db.execute(
                select(TicketMessage)
                .where(TicketMessage.ticket_id == ticket.id)
                .order_by(TicketMessage.created_at)
            )
            messages = msg_result.scalars().all()
            
            ticket_response = TicketResponse(
                id=ticket.id,
                user_id=ticket.user_id,
                subject=ticket.subject,
                status=ticket.status,
                priority=ticket.priority,
                created_at=ticket.created_at,
                updated_at=ticket.updated_at,
                messages=[TicketMessageResponse.model_validate(m) for m in messages],
            )
            ticket_responses.append(ticket_response)
        
        return ticket_responses
    except Exception as e:
        logger.error(f"Error listing all tickets: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while fetching tickets. Please try again later.",
        )


@router.patch("/{ticket_id}/status")
async def update_ticket_status(
    ticket_id: int,
    ticket_status: str = Query(..., alias="status"),
    current_user: User = Depends(get_current_support_or_superuser),
    db: AsyncSession = Depends(get_db),
):
    """Update ticket status (Close/Open)."""
    try:
    if ticket_status not in [s.value for s in TicketStatus]:
        raise HTTPException(status_code=400, detail="Invalid status")

    result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
    ticket = result.scalar_one_or_none()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    ticket.status = ticket_status
    ticket.updated_at = datetime.utcnow()
    await db.commit()

        logger.info(
            f"Ticket {ticket_id} status updated to {ticket_status} by user {current_user.id}"
        )

    return {"message": f"Ticket status updated to {ticket_status}"}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating ticket {ticket_id} status: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while updating the ticket status. Please try again later.",
        )
