from typing import Optional
import datetime

from sqlalchemy import Boolean, CHAR, CheckConstraint, Column, DateTime, ForeignKeyConstraint, Index, Integer, JSON, PrimaryKeyConstraint, SmallInteger, String, Table, Text, UniqueConstraint, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass


t_freetiles = Table(
    'freetiles', Base.metadata,
    Column('id', Integer),
    Column('title', String(80))
)


t_freetilesets = Table(
    'freetilesets', Base.metadata,
    Column('id', Integer),
    Column('name', String(80))
)


t_project_members_detailed = Table(
    'project_members_detailed', Base.metadata,
    Column('project_id', Integer),
    Column('project_name', String(80)),
    Column('user_id', Integer),
    Column('user_name', String(80)),
    Column('user_email', String(80)),
    Column('role_type', String(20)),
    Column('joined_at', DateTime),
    Column('role_priority', Integer)
)


t_project_owners_detailed = Table(
    'project_owners_detailed', Base.metadata,
    Column('project_id', Integer),
    Column('project_name', String(80)),
    Column('description', String(120)),
    Column('project_created', DateTime),
    Column('owner_id', Integer),
    Column('owner_name', String(80)),
    Column('owner_email', String(80)),
    Column('owner_company', String),
    Column('ownership_date', DateTime),
    Column('ownership_status', Text)
)


t_project_owners_summary = Table(
    'project_owners_summary', Base.metadata,
    Column('project_id', Integer),
    Column('project_name', String(80)),
    Column('creation_date', DateTime),
    Column('owner_id', Integer),
    Column('owner_name', String(80)),
    Column('owner_email', String(80)),
    Column('ownership_date', DateTime)
)


class Users(Base):
    __tablename__ = 'users'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='users_pkey'),
        UniqueConstraint('name', name='uniq_users')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    salt: Mapped[str] = mapped_column(CHAR(20), nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    creation_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    mail: Mapped[Optional[str]] = mapped_column(String(80))
    compagny: Mapped[Optional[str]] = mapped_column(String)
    manager: Mapped[Optional[str]] = mapped_column(String(80), comment='Project manager')
    password: Mapped[Optional[str]] = mapped_column(CHAR(128))
    dateverified: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    is_admin: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('false'), comment='Whether the user is an administrator')

    connections: Mapped[list['Connections']] = relationship('Connections', back_populates='users')
    projects: Mapped[list['Projects']] = relationship('Projects', back_populates='users')
    project_members_id_users: Mapped[list['ProjectMembers']] = relationship('ProjectMembers', foreign_keys='[ProjectMembers.id_users]', back_populates='users')
    project_members_user: Mapped[list['ProjectMembers']] = relationship('ProjectMembers', foreign_keys='[ProjectMembers.user_id]', back_populates='user')
    sessions: Mapped[list['Sessions']] = relationship('Sessions', secondary='many_users_has_many_sessions', back_populates='users')
    invite_links: Mapped[list['InviteLinks']] = relationship('InviteLinks', back_populates='users')


class Connections(Base):
    __tablename__ = 'connections'
    __table_args__ = (
        ForeignKeyConstraint(['id_users'], ['users.id'], ondelete='RESTRICT', onupdate='CASCADE', match='FULL', name='users_fk'),
        PrimaryKeyConstraint('id', name='connections_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_users: Mapped[int] = mapped_column(Integer, nullable=False)
    creation_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    host_address: Mapped[Optional[str]] = mapped_column(String(60))
    auth_type: Mapped[Optional[str]] = mapped_column(String(10))
    container: Mapped[Optional[str]] = mapped_column(String(100))
    scheduler: Mapped[Optional[str]] = mapped_column(String(15))
    scheduler_file: Mapped[Optional[str]] = mapped_column(String(30))
    config_files: Mapped[Optional[dict]] = mapped_column(JSON)
    connection_vnc: Mapped[Optional[int]] = mapped_column(SmallInteger, server_default=text('0'))

    users: Mapped['Users'] = relationship('Users', back_populates='connections')
    tile_sets: Mapped[Optional['TileSets']] = relationship('TileSets', uselist=False, back_populates='connections')
    tiles: Mapped[list['Tiles']] = relationship('Tiles', back_populates='connections')


class Projects(Base):
    __tablename__ = 'projects'
    __table_args__ = (
        CheckConstraint("role_type::text = ANY (ARRAY['owner'::character varying::text, 'admin'::character varying::text, 'editor'::character varying::text, 'viewer'::character varying::text, 'guest'::character varying::text])", name='valid_role_type'),
        ForeignKeyConstraint(['id_users'], ['users.id'], ondelete='SET NULL', onupdate='CASCADE', match='FULL', name='users_fk'),
        PrimaryKeyConstraint('id', name='projects_pkey'),
        UniqueConstraint('name', name='uniq_project')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    role_type: Mapped[str] = mapped_column(String(20), nullable=False, comment='Type de rôle dans le projet')
    id_users: Mapped[Optional[int]] = mapped_column(Integer)
    creation_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    description: Mapped[Optional[str]] = mapped_column(String(120))

    users: Mapped[Optional['Users']] = relationship('Users', back_populates='projects')
    project_members_id_projects: Mapped[list['ProjectMembers']] = relationship('ProjectMembers', foreign_keys='[ProjectMembers.id_projects]', back_populates='projects')
    project_members_project: Mapped[list['ProjectMembers']] = relationship('ProjectMembers', foreign_keys='[ProjectMembers.project_id]', back_populates='project')
    sessions: Mapped[list['Sessions']] = relationship('Sessions', back_populates='projects')


class ProjectMembers(Base):
    __tablename__ = 'project_members'
    __table_args__ = (
        CheckConstraint("role_type::text = ANY (ARRAY['owner'::character varying::text, 'admin'::character varying::text, 'editor'::character varying::text, 'viewer'::character varying::text, 'guest'::character varying::text])", name='valid_member_role'),
        ForeignKeyConstraint(['id_projects'], ['projects.id'], ondelete='CASCADE', onupdate='CASCADE', match='FULL', name='projects_fk'),
        ForeignKeyConstraint(['id_users'], ['users.id'], ondelete='CASCADE', onupdate='CASCADE', match='FULL', name='users_fk'),
        ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE', onupdate='CASCADE', name='project_members_project_fk'),
        ForeignKeyConstraint(['user_id'], ['users.id'], name='project_members_user_fk'),
        PrimaryKeyConstraint('project_id', 'user_id', name='project_members_pkey'),
        Index('idx_project_members_composite', 'project_id', 'user_id', 'role_type', postgresql_with={'fillfactor': '90'}),
        Index('idx_project_members_project', 'project_id', postgresql_with={'fillfactor': '90'}),
        Index('idx_project_members_project_role', 'project_id', 'role_type', postgresql_with={'fillfactor': '90'}),
        Index('idx_project_members_role', 'role_type', postgresql_where="((role_type)::text = ANY (ARRAY['owner'::text, 'admin'::text]))", postgresql_with={'fillfactor': '90'}),
        Index('idx_project_members_user', 'user_id', postgresql_with={'fillfactor': '90'}),
        Index('uq_project_owner', 'project_id', postgresql_where="((role_type)::text = 'owner'::text)", postgresql_with={'fillfactor': '90'}, unique=True)
    )

    project_id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='Reference to projects table')
    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='Reference to users table')
    role_type: Mapped[str] = mapped_column(String(20), nullable=False, server_default=text("'viewer'::character varying"), comment='Role of the user in this project')
    joined_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'), comment='When the user joined the project')
    id_users: Mapped[Optional[int]] = mapped_column(Integer)
    id_projects: Mapped[Optional[int]] = mapped_column(Integer)

    projects: Mapped[Optional['Projects']] = relationship('Projects', foreign_keys=[id_projects], back_populates='project_members_id_projects')
    users: Mapped[Optional['Users']] = relationship('Users', foreign_keys=[id_users], back_populates='project_members_id_users')
    project: Mapped['Projects'] = relationship('Projects', foreign_keys=[project_id], back_populates='project_members_project')
    user: Mapped['Users'] = relationship('Users', foreign_keys=[user_id], back_populates='project_members_user')


class Sessions(Base):
    __tablename__ = 'sessions'
    __table_args__ = (
        ForeignKeyConstraint(['id_projects'], ['projects.id'], ondelete='RESTRICT', onupdate='CASCADE', match='FULL', name='projects_fk'),
        PrimaryKeyConstraint('id', name='sessions_pkey'),
        UniqueConstraint('name', name='uniq_session')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    id_projects: Mapped[int] = mapped_column(Integer, nullable=False)
    creation_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    description: Mapped[Optional[str]] = mapped_column(String(120))
    Number_of_active_users: Mapped[Optional[int]] = mapped_column(SmallInteger, comment='Number of users actively connected to this sessions')
    timeout: Mapped[Optional[int]] = mapped_column(Integer, comment='Set the timeout (in seconds) after which a session is disactivated (Number_of_active_users is 0) while no socket is still connected.')
    config: Mapped[Optional[dict]] = mapped_column(JSON, comment='configuration of the grid for this session')

    projects: Mapped['Projects'] = relationship('Projects', back_populates='sessions')
    tile_sets: Mapped[list['TileSets']] = relationship('TileSets', secondary='many_sessions_has_many_tile_sets', back_populates='sessions')
    users: Mapped[list['Users']] = relationship('Users', secondary='many_users_has_many_sessions', back_populates='sessions')
    invite_links: Mapped[list['InviteLinks']] = relationship('InviteLinks', back_populates='sessions')


class TileSets(Base):
    __tablename__ = 'tile_sets'
    __table_args__ = (
        ForeignKeyConstraint(['id_connections'], ['connections.id'], ondelete='SET NULL', onupdate='CASCADE', match='FULL', name='connections_fk'),
        PrimaryKeyConstraint('id', name='tile_sets_pkey'),
        UniqueConstraint('id_connections', name='tile_sets_uq')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    type_of_tiles: Mapped[str] = mapped_column(String(15), nullable=False, comment='must discribe the nature sources of the tiles connected for this tile_set. In this list : web png, local image, remote database file, set of database remote files')
    Dataset_path: Mapped[Optional[str]] = mapped_column(String(100), comment='Path of  the database for this tile_set.')
    id_connections: Mapped[Optional[int]] = mapped_column(Integer)
    creation_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    source: Mapped[Optional[dict]] = mapped_column(JSON)
    config_files: Mapped[Optional[dict]] = mapped_column(JSON)
    launch_file: Mapped[Optional[str]] = mapped_column(String(30))

    sessions: Mapped[list['Sessions']] = relationship('Sessions', secondary='many_sessions_has_many_tile_sets', back_populates='tile_sets')
    connections: Mapped[Optional['Connections']] = relationship('Connections', back_populates='tile_sets')
    tiles: Mapped[list['Tiles']] = relationship('Tiles', secondary='many_tiles_has_many_tile_sets', back_populates='tile_sets')


class Tiles(Base):
    __tablename__ = 'tiles'
    __table_args__ = (
        ForeignKeyConstraint(['id_connections'], ['connections.id'], ondelete='SET NULL', onupdate='CASCADE', match='FULL', name='connections_fk'),
        PrimaryKeyConstraint('id', name='tiles_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    pos_px_x: Mapped[int] = mapped_column(Integer, nullable=False)
    pos_px_y: Mapped[int] = mapped_column(Integer, nullable=False)
    source: Mapped[dict] = mapped_column(JSON, nullable=False, comment='source of the tile : may be an url or a path in a directory of initial conditions or a list of paths.')
    title: Mapped[Optional[str]] = mapped_column(String(80))
    pos_id_x: Mapped[Optional[int]] = mapped_column(Integer)
    pos_id_y: Mapped[Optional[int]] = mapped_column(Integer)
    comment: Mapped[Optional[str]] = mapped_column(Text)
    tags: Mapped[Optional[dict]] = mapped_column(JSON)
    id_connections: Mapped[Optional[int]] = mapped_column(Integer)
    creation_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    IdLocation: Mapped[Optional[int]] = mapped_column(SmallInteger)

    tile_sets: Mapped[list['TileSets']] = relationship('TileSets', secondary='many_tiles_has_many_tile_sets', back_populates='tiles')
    connections: Mapped[Optional['Connections']] = relationship('Connections', back_populates='tiles')


class InviteLinks(Base):
    __tablename__ = 'invite_links'
    __table_args__ = (
        ForeignKeyConstraint(['id_sessions'], ['sessions.id'], ondelete='SET NULL', onupdate='CASCADE', match='FULL', name='sessions_fk'),
        ForeignKeyConstraint(['id_users'], ['users.id'], ondelete='SET NULL', onupdate='CASCADE', match='FULL', name='users_fk'),
        PrimaryKeyConstraint('id', name='invite_links_pkey'),
        UniqueConstraint('link', name='invite_links_link_key')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    link: Mapped[str] = mapped_column(String(200), nullable=False)
    host_user: Mapped[str] = mapped_column(String(80), nullable=False)
    host_project: Mapped[str] = mapped_column(String(80), nullable=False)
    type: Mapped[Optional[bool]] = mapped_column(Boolean)
    creation_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    expiration_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='Date after which the invite link expires')
    is_revoked: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('false'), comment='Whether the invite link has been revoked')
    message: Mapped[Optional[str]] = mapped_column(String(500), comment='Custom message to be sent with the invitation')
    target_email: Mapped[Optional[str]] = mapped_column(String(80), comment='Email address of the invited user')
    group_name: Mapped[Optional[str]] = mapped_column(String(80), comment='Name of the group if this is a group invitation')
    id_sessions: Mapped[Optional[int]] = mapped_column(Integer)
    id_users: Mapped[Optional[int]] = mapped_column(Integer)
    max_uses: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('1'), comment='Maximum number of times this invite link can be used')
    use_count: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('0'), comment='Number of times this invite link has been used')

    sessions: Mapped[Optional['Sessions']] = relationship('Sessions', back_populates='invite_links')
    users: Mapped[Optional['Users']] = relationship('Users', back_populates='invite_links')


t_many_sessions_has_many_tile_sets = Table(
    'many_sessions_has_many_tile_sets', Base.metadata,
    Column('id_sessions', Integer, primary_key=True),
    Column('id_tile_sets', Integer, primary_key=True),
    ForeignKeyConstraint(['id_sessions'], ['sessions.id'], ondelete='RESTRICT', onupdate='CASCADE', match='FULL', name='sessions_fk'),
    ForeignKeyConstraint(['id_tile_sets'], ['tile_sets.id'], ondelete='RESTRICT', onupdate='CASCADE', match='FULL', name='tile_sets_fk'),
    PrimaryKeyConstraint('id_sessions', 'id_tile_sets', name='many_sessions_has_many_tile_sets_pk')
)


t_many_tiles_has_many_tile_sets = Table(
    'many_tiles_has_many_tile_sets', Base.metadata,
    Column('id_tiles', Integer, primary_key=True),
    Column('id_tile_sets', Integer, primary_key=True),
    ForeignKeyConstraint(['id_tile_sets'], ['tile_sets.id'], ondelete='RESTRICT', onupdate='CASCADE', match='FULL', name='tile_sets_fk'),
    ForeignKeyConstraint(['id_tiles'], ['tiles.id'], ondelete='RESTRICT', onupdate='CASCADE', match='FULL', name='tiles_fk'),
    PrimaryKeyConstraint('id_tiles', 'id_tile_sets', name='many_tiles_has_many_tile_sets_pk')
)


t_many_users_has_many_sessions = Table(
    'many_users_has_many_sessions', Base.metadata,
    Column('id_users', Integer, primary_key=True),
    Column('id_sessions', Integer, primary_key=True),
    ForeignKeyConstraint(['id_sessions'], ['sessions.id'], ondelete='RESTRICT', onupdate='CASCADE', match='FULL', name='sessions_fk'),
    ForeignKeyConstraint(['id_users'], ['users.id'], ondelete='RESTRICT', onupdate='CASCADE', match='FULL', name='users_fk'),
    PrimaryKeyConstraint('id_users', 'id_sessions', name='many_users_has_many_sessions_pk')
)
