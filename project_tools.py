"""Project management tools for Jira Cloud."""

import json
from jira_client import JiraCloudClient

def _fmt(data) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


def register_project_tools(mcp, client: JiraCloudClient):

    DEFAULT_TEMPLATE_KEYS = {
        "software": "com.pyxis.greenhopper.jira:gh-simplified-agility-scrum",
        "service_desk": "com.atlassian.servicedesk:simplified-it-service-management",
        "business": "com.atlassian.jira-core-project-templates:jira-core-simplified-task-tracking",
    }

    @mcp.tool()
    async def create_project(key: str, name: str, project_type: str = "software",
                             lead_account_id: str = "", description: str = "",
                             template_key: str = "") -> str:
        """Create a new Jira project.

        Args:
            key: Project key (e.g. 'HR', 'DEV') — uppercase, 2-10 chars
            name: Project name
            project_type: 'software', 'service_desk', or 'business'
            lead_account_id: Account ID of project lead (empty = current user)
            description: Project description
            template_key: Explicit projectTemplateKey. Overrides the per-type default,
                which is only one of several templates each type offers — an ITSM default
                is wrong for, say, a general or internal service desk. List the templates
                your site actually offers with list_project_templates before picking one.
        """
        body = {
            "key": key.upper(),
            "name": name,
            "projectTypeKey": project_type,
            "projectTemplateKey": template_key or DEFAULT_TEMPLATE_KEYS.get(
                project_type, DEFAULT_TEMPLATE_KEYS["business"]
            ),
        }
        if lead_account_id:
            body["leadAccountId"] = lead_account_id
        else:
            me = await client.get("/myself")
            body["leadAccountId"] = me["accountId"]
        if description:
            body["description"] = description
        data = await client.post("/project", body)
        return _fmt(data)

    @mcp.tool()
    async def list_project_templates() -> str:
        """List the project types and templates this site offers.

        Use before create_project to pick the right template_key rather than
        accepting the per-type default.
        """
        types = await client.get("/project/type")
        return _fmt(types)

    @mcp.tool()
    async def list_projects(search: str = "") -> str:
        """List all projects."""
        params = {"maxResults": 200}
        if search:
            params["query"] = search
        data = await client.get("/project/search", **params)
        return _fmt(data.get("values", []))

    @mcp.tool()
    async def get_project(project_key: str) -> str:
        """Get project details with all components, versions, roles."""
        data = await client.get(f"/project/{project_key}", expand="lead,description,url")
        return _fmt(data)

    @mcp.tool()
    async def get_project_roles(project_key: str) -> str:
        """Get all roles for a project with members."""
        roles = await client.get(f"/project/{project_key}/role")
        result = {}
        for role_name, role_url in roles.items():
            role_id = role_url.rstrip("/").split("/")[-1]
            try:
                role_data = await client.get(f"/project/{project_key}/role/{role_id}")
                result[role_name] = role_data
            except Exception:
                result[role_name] = {"id": role_id}
        return _fmt(result)

    @mcp.tool()
    async def add_project_role_member(project_key: str, role_id: str, account_id: str = "", group_name: str = "") -> str:
        """Add user or group to a project role."""
        body = {}
        if account_id:
            body["user"] = [account_id]
        if group_name:
            body["group"] = [group_name]
        data = await client.post(f"/project/{project_key}/role/{role_id}", body)
        return _fmt(data)

    @mcp.tool()
    async def remove_project_role_member(project_key: str, role_id: str, account_id: str = "", group_name: str = "") -> str:
        """Remove user or group from a project role."""
        params = ""
        if account_id:
            params = f"?user={account_id}"
        elif group_name:
            params = f"?group={group_name}"
        await client.delete(f"/project/{project_key}/role/{role_id}{params}")
        return _fmt({"status": "removed"})

    @mcp.tool()
    async def list_project_roles_global() -> str:
        """List all project roles (global definitions)."""
        data = await client.get("/role")
        return _fmt(data)

    @mcp.tool()
    async def create_component(project_key: str, name: str, description: str = "", lead: str = "") -> str:
        """Create a project component."""
        body = {"name": name, "project": project_key}
        if description:
            body["description"] = description
        if lead:
            body["leadAccountId"] = lead
        data = await client.post("/component", body)
        return _fmt(data)

    @mcp.tool()
    async def list_components(project_key: str) -> str:
        """List project components."""
        data = await client.get(f"/project/{project_key}/components")
        return _fmt(data)

    @mcp.tool()
    async def create_version(project_key: str, name: str, description: str = "",
                             start_date: str = "", release_date: str = "") -> str:
        """Create a project version."""
        body = {"name": name, "projectId": None}
        # Get project ID
        proj = await client.get(f"/project/{project_key}")
        body["projectId"] = int(proj["id"])
        if description:
            body["description"] = description
        if start_date:
            body["startDate"] = start_date
        if release_date:
            body["releaseDate"] = release_date
        data = await client.post("/version", body)
        return _fmt(data)

    @mcp.tool()
    async def list_versions(project_key: str) -> str:
        """List project versions."""
        data = await client.get(f"/project/{project_key}/versions")
        return _fmt(data)

    @mcp.tool()
    async def get_project_config(project_key: str) -> str:
        """Get full project configuration — permission scheme, notification scheme,
        issue type scheme, workflow scheme, and other assigned schemes."""
        result = {}
        result["project"] = await client.get(f"/project/{project_key}")
        # Permission scheme
        try:
            ps = await client.raw_get(f"/rest/api/3/project/{project_key}/permissionscheme")
            result["permissionScheme"] = ps
        except Exception:
            pass
        # Notification scheme
        try:
            ns = await client.raw_get(f"/rest/api/3/project/{project_key}/notificationscheme")
            result["notificationScheme"] = ns
        except Exception:
            pass
        # Issue security scheme
        try:
            ss = await client.raw_get(f"/rest/api/3/project/{project_key}/issuesecuritylevelscheme")
            result["securityScheme"] = ss
        except Exception:
            pass
        # Components
        try:
            result["components"] = await client.get(f"/project/{project_key}/components")
        except Exception:
            pass
        # Versions
        try:
            result["versions"] = await client.get(f"/project/{project_key}/versions")
        except Exception:
            pass
        # Roles
        try:
            result["roles"] = await client.get(f"/project/{project_key}/role")
        except Exception:
            pass
        return _fmt(result)
