# -*- coding: utf-8; -*-
################################################################################
#
#  Wutta-Continuum -- SQLAlchemy Versioning for Wutta Framework
#  Copyright © 2024-2025 Lance Edgar
#
#  This file is part of Wutta Framework.
#
#  Wutta Framework is free software: you can redistribute it and/or modify it
#  under the terms of the GNU General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option) any
#  later version.
#
#  Wutta Framework is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
#  FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
#  more details.
#
#  You should have received a copy of the GNU General Public License along with
#  Wutta Framework.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
App Configuration
"""

import socket

from sqlalchemy.orm import configure_mappers
from sqlalchemy_continuum import make_versioned
from sqlalchemy_continuum.plugins import Plugin, TransactionMetaPlugin

from wuttjamaican.conf import WuttaConfigExtension
from wuttjamaican.util import load_object


class WuttaContinuumConfigExtension(WuttaConfigExtension):
    """
    App :term:`config extension` for Wutta-Continuum.

    This adds a startup hook, which can optionally turn on the
    SQLAlchemy-Continuum versioning features for the main app DB.
    """

    key = "wutta_continuum"

    def startup(self, config):  # pylint: disable=empty-docstring
        """
        Perform final configuration setup for app startup.

        This will do nothing at all, unless config enables the
        versioning feature.  This must be done in config file and not
        in DB settings table:

        .. code-block:: ini

           [wutta_continuum]
           enable_versioning = true

        Once enabled, this method will configure the integration, via
        these steps:

        1. call :func:`sqlalchemy-continuum:sqlalchemy_continuum.make_versioned()`
        2. call :meth:`wuttjamaican:wuttjamaican.app.AppHandler.get_model()`
        3. call :func:`sqlalchemy:sqlalchemy.orm.configure_mappers()`

        For more about SQLAlchemy-Continuum see
        :doc:`sqlalchemy-continuum:intro`.

        Two plugins are provided to ``make_versioned()``:

        The first is ``TransactionMetaPlugin`` for sake of adding
        comments (see
        :mod:`~sqlalchemy-continuum:sqlalchemy_continuum.plugins.transaction_meta`).

        The second by default is :class:`WuttaContinuumPlugin` but you
        can override with config:

        .. code-block:: ini

           [wutta_continuum]
           wutta_plugin_spec = poser.db.continuum:PoserContinuumPlugin

        See also the SQLAlchemy-Continuum docs for
        :doc:`sqlalchemy-continuum:plugins`.
        """
        # only do this if config enables it
        if not config.get_bool(
            "wutta_continuum.enable_versioning", usedb=False, default=False
        ):
            return

        # create wutta plugin, to assign user and ip address
        spec = config.get(
            "wutta_continuum.wutta_plugin_spec",
            usedb=False,
            default="wutta_continuum.conf:WuttaContinuumPlugin",
        )
        plugin = load_object(spec)

        app = config.get_app()
        if "model" in app.__dict__:
            raise RuntimeError("something not right, app already has model")

        # let sqlalchemy-continuum do its thing
        make_versioned(plugins=[TransactionMetaPlugin(), plugin()])

        # must load model *between* prev and next calls
        app.get_model()

        # let sqlalchemy do its thing
        configure_mappers()


class WuttaContinuumPlugin(Plugin):
    """
    SQLAlchemy-Continuum manager plugin for Wutta-Continuum.

    This is the default plugin used within
    :meth:`~WuttaContinuumConfigExtension.startup()` unless config
    overrides.

    This tries to establish the user and IP address responsible, and
    comment if applicable, for the current transaction.

    See also the SQLAlchemy-Continuum docs for
    :doc:`sqlalchemy-continuum:plugins`.
    """

    def get_remote_addr(self, uow, session):  # pylint: disable=unused-argument
        """
        This should return the effective IP address responsible for
        the current change(s).

        Default logic will assume the "current machine" e.g. where a
        CLI command or script is running.  In practice that often
        means this winds up being ``127.0.0.1`` or similar.

        :returns: IP address (v4 or v6) as string
        """
        host = socket.gethostname()
        return socket.gethostbyname(host)

    def get_user_id(self, uow, session):  # pylint: disable=unused-argument
        """
        This should return the effective ``User.uuid`` indicating who
        is responsible for the current change(s).

        Default logic does not have a way to determine current user on
        its own per se.  However it can inspect the session, and use a
        value from there if found.

        Any session can therefore declare the resonsible user::

           myuser = session.query(model.User).first()
           session.info["continuum_user_id"] = myuser.uuid

        :returns: :attr:`wuttjamaican.db.model.auth.User.uuid` value,
           or ``None``
        """
        if user_id := session.info.get("continuum_user_id"):
            return user_id

        return None

    def transaction_args(self, uow, session):
        """
        This is a standard hook method for SQLAchemy-Continuum
        plugins.  We use it to (try to) inject these values, which
        then become set on the current (new) transaction:

        * ``remote_addr`` - effective IP address causing the change
           * see :meth:`get_remote_addr()`
        * ``user_id`` - effective ``User.uuid`` for change authorship
           * see :meth:`get_user_id()`
        """
        kwargs = {}

        remote_addr = self.get_remote_addr(uow, session)
        if remote_addr:
            kwargs["remote_addr"] = remote_addr

        user_id = self.get_user_id(uow, session)  # pylint: disable=assignment-from-none
        if user_id:
            kwargs["user_id"] = user_id

        return kwargs

    def before_flush(self, uow, session):
        """
        We use this hook to inject the "comment" for current
        transaction, if applicable.

        This checks the session for the comment; so any session can
        specify one like so::

           session.info["continuum_comment"] = "hello world"
        """
        if comment := session.info.get("continuum_comment"):
            uow.current_transaction.meta["comment"] = comment
