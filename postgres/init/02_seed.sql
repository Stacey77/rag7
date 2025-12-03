-- Seed data for development and testing

-- Create default super admin user
INSERT INTO users (id, email, hashed_password, full_name, is_active, is_superuser, email_verified) 
VALUES (
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
    'admin@ragamuffin.ai',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5pGfW.n8Hg7iK', -- password: admin123
    'System Administrator',
    true,
    true,
    true
) ON CONFLICT (email) DO NOTHING;

-- Create demo organization
INSERT INTO organizations (id, name, slug, plan, max_workspaces, max_users, storage_quota_gb, is_active) 
VALUES (
    'b1ffbc99-9c0b-4ef8-bb6d-6bb9bd380a22',
    'Demo Organization',
    'demo-org',
    'enterprise',
    100,
    100,
    1000,
    true
) ON CONFLICT (slug) DO NOTHING;

-- Add admin as owner of demo organization
INSERT INTO organization_members (organization_id, user_id, role, invited_by) 
VALUES (
    'b1ffbc99-9c0b-4ef8-bb6d-6bb9bd380a22',
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
    'owner',
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'
) ON CONFLICT (organization_id, user_id) DO NOTHING;

-- Create demo workspaces
INSERT INTO workspaces (id, organization_id, name, slug, description, is_active) 
VALUES 
    (
        'c2ffbc99-9c0b-4ef8-bb6d-6bb9bd380a33',
        'b1ffbc99-9c0b-4ef8-bb6d-6bb9bd380a22',
        'Main Project',
        'main-project',
        'Primary workspace for demonstration',
        true
    ),
    (
        'd3ffbc99-9c0b-4ef8-bb6d-6bb9bd380a44',
        'b1ffbc99-9c0b-4ef8-bb6d-6bb9bd380a22',
        'Test Environment',
        'test-env',
        'Testing and experimentation workspace',
        true
    )
ON CONFLICT (organization_id, slug) DO NOTHING;

-- Add admin to workspaces
INSERT INTO workspace_members (workspace_id, user_id, role) 
VALUES 
    (
        'c2ffbc99-9c0b-4ef8-bb6d-6bb9bd380a33',
        'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
        'admin'
    ),
    (
        'd3ffbc99-9c0b-4ef8-bb6d-6bb9bd380a44',
        'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
        'admin'
    )
ON CONFLICT (workspace_id, user_id) DO NOTHING;

-- Create default model
INSERT INTO models (id, organization_id, name, type, version, dimension, is_active, is_default, created_by) 
VALUES (
    'e4ffbc99-9c0b-4ef8-bb6d-6bb9bd380a55',
    NULL, -- NULL means available to all organizations
    'all-MiniLM-L6-v2',
    'sentence-transformer',
    'v2.2.0',
    384,
    true,
    true,
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'
) ON CONFLICT (id) DO NOTHING;

-- Create sample collection
INSERT INTO collections (id, workspace_id, name, milvus_collection_name, model_id, dimension) 
VALUES (
    'f5ffbc99-9c0b-4ef8-bb6d-6bb9bd380a66',
    'c2ffbc99-9c0b-4ef8-bb6d-6bb9bd380a33',
    'text_embeddings',
    'workspace_c2ffbc99_text_embeddings',
    'e4ffbc99-9c0b-4ef8-bb6d-6bb9bd380a55',
    384
) ON CONFLICT (workspace_id, name) DO NOTHING;

-- Log initial setup in audit logs
INSERT INTO audit_logs (organization_id, user_id, action, resource_type, details) 
VALUES (
    'b1ffbc99-9c0b-4ef8-bb6d-6bb9bd380a22',
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
    'system_initialized',
    'system',
    '{"message": "Initial database setup completed", "version": "1.0.0"}'::jsonb
);
