import pytest

from apibean.pytest.decorators import concrete_fixture

@pytest.fixture(scope="function")
@concrete_fixture
def login(apibean_container):
    """
    Fixture that provides a helper function for user authentication.

    This fixture returns a callable `_login` which performs a login operation
    using the `AuthService` obtained from `apibean_container` and returns
    an access token. It helps avoid duplicating authentication logic
    across test cases.

    Returns:
        Callable[[str, str], str]:
            A function `_login(username, password)` that authenticates
            the given credentials and returns an access token string.

    Example:
        def test_authenticated_endpoint(login, api_client):
            token = login("admin", "secret")
            response = api_client.get(
                "/protected",
                headers={"Authorization": f"Bearer {token}"}
            )
            assert response.status_code == 200
    """
    def _login(username: str, password: str) -> str:
        auth_service = apibean_container.auth_service()
        result = auth_service.login(dict(username=username, password=password))
        return result["access_token"]
    return _login


@pytest.fixture(scope="function")
@concrete_fixture
def login_with_deprecated_key(apibean_container):
    """
    Fixture that provides a helper function to authenticate using
    a deprecated secret key.

    This fixture returns a callable `_login` that performs authentication
    via `AuthService.deprecated_login`, allowing the system to issue an
    access token using the deprecated (previous) secret key.

    The application supports secret key rotation by allowing two keys
    to coexist temporarily (current and deprecated). This fixture is
    intended for testing backward compatibility during key rotation,
    ensuring that existing clients continue to function without
    service interruption.

    Returns:
        Callable[[str, str], str]:
            A function `_login(username, password)` that authenticates
            using the deprecated secret key and returns an access token.

    Example:
        def test_backward_compatible_login(
            login_with_deprecated_key, api_client
        ):
            token = login_with_deprecated_key("legacy.user", "secret")
            response = api_client.get(
                "/health",
                headers={"Authorization": f"Bearer {token}"}
            )
            assert response.status_code == 200

    Notes:
        - This fixture should only be used for compatibility and migration
          tests related to secret key rotation.
        - New integrations should use the standard `login` fixture instead.
    """
    def _login(username: str, password: str) -> str:
        auth_service = apibean_container.auth_service()
        result = auth_service.deprecated_login(dict(username=username, password=password))
        assert result is not None, f"auth_service.login() failed: { result }"
        return result["access_token"]

    return _login


@pytest.fixture(scope="function")
@concrete_fixture
def login_as_delegate(apibean_container):
    """
    Fixture that provides a helper function for delegated authentication
    into an organization.

    This fixture returns a callable `_login` that allows a user who is not
    a direct member of an organization to log in with a delegated role.
    Such delegation must be pre-authorized by the organization owner and
    is typically used for scenarios like technical support access,
    internship programs, or guest accounts.

    The delegated login is performed in the context of a specific
    organization, identified by its slug, and results in an access token
    scoped to the delegated role.

    Returns:
        Callable[[str, str, str], str]:
            A function `_login(username, password, org_slug)` that performs
            delegated authentication and returns an access token.

    Example:
        def test_support_user_access(
            login_as_delegate, api_client
        ):
            token = login_as_delegate(
                "support.user@example.com",
                "secret",
                "acme-org",
            )
            response = api_client.get(
                "/org/acme-org/dashboard",
                headers={"Authorization": f"Bearer {token}"}
            )
            assert response.status_code == 200

    Notes:
        - The user must be explicitly delegated by the organization owner
          prior to login.
        - The returned access token reflects the delegated role and
          permissions, not full organization membership.
    """
    def _login(username: str, password: str, org_slug: str) -> str:
        org_service = apibean_container.org_service()
        org_id = org_service.get_id_by_slug(org_slug)
        auth_service = apibean_container.auth_service()
        result = auth_service.delegated_login(dict(
            org_slug=org_slug,
            username=username,
            password=password))
        assert result is not None, f"auth_service.delegated_login() failed: { result }"
        return result["access_token"]

    return _login


@pytest.fixture(scope="function")
@concrete_fixture
def root_access_token(login, apibean_safe_config):
    """
    Fixture that provides an access token for the root user.

    This fixture logs in using the root user credentials defined in
    `apibean_safe_config` and returns the corresponding access token.
    It is typically used for test cases that require elevated
    or administrative privileges.

    Returns:
        str:
            Access token string for the root user.

    Example:
        def test_admin_only_endpoint(root_access_token, api_client):
            response = api_client.get(
                "/admin/stats",
                headers={"Authorization": f"Bearer {root_access_token}"}
            )
            assert response.status_code == 200
    """
    return login(apibean_safe_config.ROOT_USER_EMAIL, apibean_safe_config.ROOT_USER_PASSWORD)


@pytest.fixture(scope="function")
@concrete_fixture
def sync_access_token(login, apibean_safe_config):
    """
    Fixture that provides an access token for the SYNC user.

    The SYNC user is a special type of ROOT account dedicated to
    synchronizing data from external systems into the application.
    This fixture authenticates using the SYNC user credentials defined
    in `apibean_safe_config` and returns the corresponding access token.

    It is intended for test cases that cover data synchronization flows,
    background jobs, or system-to-system integrations requiring
    elevated privileges.

    Returns:
        str:
            Access token string for the SYNC (ROOT-level) user.

    Example:
        def test_sync_job(sync_access_token, api_client):
            response = api_client.post(
                "/sync/import",
                headers={"Authorization": f"Bearer {sync_access_token}"}
            )
            assert response.status_code == 200
    """
    return login(apibean_safe_config.SYNC_USER_EMAIL, apibean_safe_config.SYNC_USER_PASSWORD)


@pytest.fixture(scope="function")
@concrete_fixture
def inject_access_token():
    """
    Fixture that provides a helper function to inject a Bearer access token
    into HTTP request headers.

    This fixture returns a callable `_inject_access_token` which takes an
    access token and an optional headers dictionary, then injects the
    `Authorization: Bearer <token>` header and returns the updated headers.

    Note:
        This fixture is planned to be deprecated and renamed to
        `gen_authorization_headers`. New test code should prefer the
        upcoming fixture name for clarity and consistency.

    Returns:
        Callable[[str, Optional[dict]], dict]:
            A function `_inject_access_token(access_token, headers=None)`
            that returns a headers dictionary containing the
            `Authorization` header.

    Example:
        def test_authorized_request(
            api_client, root_access_token, inject_access_token
        ):
            headers = inject_access_token(root_access_token)
            response = api_client.get("/protected", headers=headers)
            assert response.status_code == 200
    """
    def _inject_access_token(access_token, headers = None):
        headers = headers or {}
        headers.update({
            "Authorization": f"Bearer {access_token}"
        })
        return headers
    return _inject_access_token
