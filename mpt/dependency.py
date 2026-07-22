def missing_dependencies(package, installed_db):
    missing = []
    for dependency in package.dependencies:
        if not installed_db.get_package(dependency):
            missing.append(dependency)
    return missing
