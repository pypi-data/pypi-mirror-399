import os


def check_package_structure(
    base_path: str, expected_folders: list[str]
) -> dict[str, bool]:
    """Checks if the required folders exist in the project structure.

    Args:
        base_path (str): The root path of the project.
        expected_folders (list[str]): A list of folder names that should exist.

    Returns:
        dict[str, bool]: A mapping where the key is the folder name and the value
            indicates its existence.
    """
    results: dict[str, bool] = {}
    for folder in expected_folders:
        path: str = os.path.join(base_path, folder)
        results[folder] = os.path.isdir(path)
    return results


def validate_environment(variables: list[str]) -> set[str]:
    """Identifies missing environment variables from a required list.

    Args:
        variables (list[str]): The names of the environment variables to check.

    Returns:
        set[str]: A set of variable names that are not defined in the environment.
    """
    missing_vars: set[str] = {var for var in variables if var not in os.environ}
    return missing_vars


if __name__ == "__main__":
    # Example usage for package internal validation
    folders_to_check: list[str] = ["src", "dist"]
    required_env: list[str] = ["GITHUB_TOKEN", "MY_NEW_TOKEN"]

    print(f"Structure Status: {check_package_structure('.', folders_to_check)}")
    print(f"Missing Env Vars: {validate_environment(required_env)}")
