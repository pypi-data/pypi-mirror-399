from .db.migrate_receiver import create_permissions_receiver


DEFAULT_PERMISSIONS = [
    ('tenant.read', 'Read permission for tenants'),
    ('tenant.write', 'Write permission for tenants'),
    ('tenant.admin', 'Admin permission for tenants'),
]

create_permissions = create_permissions_receiver(DEFAULT_PERMISSIONS)
