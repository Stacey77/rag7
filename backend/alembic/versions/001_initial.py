"""Initial migration - create core tables

Revision ID: 001_initial
Revises: 
Create Date: 2025-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum types
    op.execute("CREATE TYPE taskstate AS ENUM ('queued', 'assigned', 'acked', 'in_progress', 'completed', 'verified', 'failed', 'escalated')")
    op.execute("CREATE TYPE agenttype AS ENUM ('communication', 'decision', 'delegation', 'learning')")
    
    # Create models table
    op.create_table(
        'models',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('version', sa.String(length=50), nullable=False),
        sa.Column('agent_type', sa.Enum('communication', 'decision', 'delegation', 'learning', name='agenttype'), nullable=False),
        sa.Column('model_path', sa.String(length=500), nullable=True),
        sa.Column('model_url', sa.String(length=500), nullable=True),
        sa.Column('metrics', sa.JSON(), nullable=True),
        sa.Column('training_job_id', sa.String(length=100), nullable=True),
        sa.Column('trained_on_feedback_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('training_started_at', sa.DateTime(), nullable=True),
        sa.Column('training_completed_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('deployed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('training_job_id')
    )
    op.create_index(op.f('ix_models_name'), 'models', ['name'], unique=False)
    op.create_index(op.f('ix_models_agent_type'), 'models', ['agent_type'], unique=False)
    
    # Create agents table
    op.create_table(
        'agents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('agent_type', sa.Enum('communication', 'decision', 'delegation', 'learning', name='agenttype'), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('version', sa.String(length=50), nullable=False),
        sa.Column('is_active', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('current_load', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('max_load', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('current_model_id', sa.Integer(), nullable=True),
        sa.Column('config', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['current_model_id'], ['models.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_agents_name'), 'agents', ['name'], unique=True)
    op.create_index(op.f('ix_agents_agent_type'), 'agents', ['agent_type'], unique=False)
    
    # Create tasks table
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('task_type', sa.String(length=100), nullable=False),
        sa.Column('state', sa.Enum('queued', 'assigned', 'acked', 'in_progress', 'completed', 'verified', 'failed', 'escalated', name='taskstate'), nullable=False, server_default='queued'),
        sa.Column('priority', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('input_data', sa.JSON(), nullable=False),
        sa.Column('output_data', sa.JSON(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('assigned_agent_id', sa.Integer(), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('max_retries', sa.Integer(), nullable=False, server_default='3'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('assigned_at', sa.DateTime(), nullable=True),
        sa.Column('acked_at', sa.DateTime(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('escalated_at', sa.DateTime(), nullable=True),
        sa.Column('ack_timeout_seconds', sa.Integer(), nullable=False, server_default='30'),
        sa.Column('task_timeout_seconds', sa.Integer(), nullable=False, server_default='300'),
        sa.ForeignKeyConstraint(['assigned_agent_id'], ['agents.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tasks_task_type'), 'tasks', ['task_type'], unique=False)
    op.create_index(op.f('ix_tasks_state'), 'tasks', ['state'], unique=False)
    op.create_index(op.f('ix_tasks_priority'), 'tasks', ['priority'], unique=False)
    op.create_index(op.f('ix_tasks_assigned_agent_id'), 'tasks', ['assigned_agent_id'], unique=False)
    
    # Create events table
    op.create_table(
        'events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('event_data', sa.JSON(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('task_id', sa.Integer(), nullable=True),
        sa.Column('agent_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ),
        sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_events_event_type'), 'events', ['event_type'], unique=False)
    op.create_index(op.f('ix_events_timestamp'), 'events', ['timestamp'], unique=False)
    op.create_index(op.f('ix_events_task_id'), 'events', ['task_id'], unique=False)
    op.create_index(op.f('ix_events_agent_id'), 'events', ['agent_id'], unique=False)
    op.create_index(op.f('ix_events_user_id'), 'events', ['user_id'], unique=False)
    
    # Create audits table
    op.create_table(
        'audits',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('user_id', sa.String(length=100), nullable=False),
        sa.Column('user_role', sa.String(length=50), nullable=False),
        sa.Column('task_id', sa.Integer(), nullable=True),
        sa.Column('resource_type', sa.String(length=50), nullable=True),
        sa.Column('resource_id', sa.String(length=100), nullable=True),
        sa.Column('details', sa.JSON(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('ip_address', sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audits_action'), 'audits', ['action'], unique=False)
    op.create_index(op.f('ix_audits_user_id'), 'audits', ['user_id'], unique=False)
    op.create_index(op.f('ix_audits_timestamp'), 'audits', ['timestamp'], unique=False)
    op.create_index(op.f('ix_audits_task_id'), 'audits', ['task_id'], unique=False)
    
    # Create feedback table
    op.create_table(
        'feedback',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(length=100), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=True),
        sa.Column('feedback_type', sa.String(length=50), nullable=False),
        sa.Column('feedback_text', sa.Text(), nullable=True),
        sa.Column('feedback_data', sa.JSON(), nullable=True),
        sa.Column('used_for_training', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('training_job_id', sa.String(length=100), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_feedback_task_id'), 'feedback', ['task_id'], unique=False)
    op.create_index(op.f('ix_feedback_user_id'), 'feedback', ['user_id'], unique=False)
    op.create_index(op.f('ix_feedback_timestamp'), 'feedback', ['timestamp'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index(op.f('ix_feedback_timestamp'), table_name='feedback')
    op.drop_index(op.f('ix_feedback_user_id'), table_name='feedback')
    op.drop_index(op.f('ix_feedback_task_id'), table_name='feedback')
    op.drop_table('feedback')
    
    op.drop_index(op.f('ix_audits_task_id'), table_name='audits')
    op.drop_index(op.f('ix_audits_timestamp'), table_name='audits')
    op.drop_index(op.f('ix_audits_user_id'), table_name='audits')
    op.drop_index(op.f('ix_audits_action'), table_name='audits')
    op.drop_table('audits')
    
    op.drop_index(op.f('ix_events_user_id'), table_name='events')
    op.drop_index(op.f('ix_events_agent_id'), table_name='events')
    op.drop_index(op.f('ix_events_task_id'), table_name='events')
    op.drop_index(op.f('ix_events_timestamp'), table_name='events')
    op.drop_index(op.f('ix_events_event_type'), table_name='events')
    op.drop_table('events')
    
    op.drop_index(op.f('ix_tasks_assigned_agent_id'), table_name='tasks')
    op.drop_index(op.f('ix_tasks_priority'), table_name='tasks')
    op.drop_index(op.f('ix_tasks_state'), table_name='tasks')
    op.drop_index(op.f('ix_tasks_task_type'), table_name='tasks')
    op.drop_table('tasks')
    
    op.drop_index(op.f('ix_agents_agent_type'), table_name='agents')
    op.drop_index(op.f('ix_agents_name'), table_name='agents')
    op.drop_table('agents')
    
    op.drop_index(op.f('ix_models_agent_type'), table_name='models')
    op.drop_index(op.f('ix_models_name'), table_name='models')
    op.drop_table('models')
    
    # Drop enum types
    op.execute("DROP TYPE agenttype")
    op.execute("DROP TYPE taskstate")
