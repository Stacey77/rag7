"""Initial schema for RAG7 agent system

Revision ID: 001
Revises: 
Create Date: 2024-12-19 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create agent_sessions table
    op.create_table(
        'agent_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('agent_name', sa.String(255), nullable=False),
        sa.Column('session_type', sa.String(50), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('metadata', postgresql.JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    
    op.create_index('idx_agent_sessions_agent_name', 'agent_sessions', ['agent_name'])
    op.create_index('idx_agent_sessions_status', 'agent_sessions', ['status'])
    op.create_index('idx_agent_sessions_started_at', 'agent_sessions', ['started_at'])
    
    # Create agent_tasks table
    op.create_table(
        'agent_tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('agent_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('task_type', sa.String(100), nullable=False),
        sa.Column('input_data', postgresql.JSONB, nullable=False),
        sa.Column('output_data', postgresql.JSONB, nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('duration_ms', sa.Integer, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    
    op.create_index('idx_agent_tasks_session_id', 'agent_tasks', ['session_id'])
    op.create_index('idx_agent_tasks_task_type', 'agent_tasks', ['task_type'])
    op.create_index('idx_agent_tasks_status', 'agent_tasks', ['status'])
    
    # Create llm_api_calls table
    op.create_table(
        'llm_api_calls',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('agent_tasks.id', ondelete='SET NULL'), nullable=True),
        sa.Column('model', sa.String(100), nullable=False),
        sa.Column('provider', sa.String(50), nullable=False),
        sa.Column('prompt_tokens', sa.Integer, nullable=False),
        sa.Column('completion_tokens', sa.Integer, nullable=False),
        sa.Column('total_tokens', sa.Integer, nullable=False),
        sa.Column('cost_usd', sa.Numeric(10, 6), nullable=False),
        sa.Column('latency_ms', sa.Integer, nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    
    op.create_index('idx_llm_api_calls_model', 'llm_api_calls', ['model'])
    op.create_index('idx_llm_api_calls_provider', 'llm_api_calls', ['provider'])
    op.create_index('idx_llm_api_calls_created_at', 'llm_api_calls', ['created_at'])
    op.create_index('idx_llm_api_calls_task_id', 'llm_api_calls', ['task_id'])


def downgrade() -> None:
    op.drop_table('llm_api_calls')
    op.drop_table('agent_tasks')
    op.drop_table('agent_sessions')
