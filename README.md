# MagicaVoxel OBJ UV mapping correcture

This script allows to correct the UV mapping of OBJs exported from MagicaVoxel.

Unfortunately MagicaVoxel maps the UV coordinates to points instead of areas. This makes no sense for a model and it also creates issues with Minecraft shaders.

## How to use
Use the CMD to execute the script like this:

`python __init__.py "path/to/model.obj"`

The script will then overwrite the specified OBJ file. It is recommended to directly convert the OBJ after exporting from MagicaVoxel.

If you want to create a new OBJ file instead of overwriting, you can specify it after the target file like this:

`python __init__.py "path/to/model.obj" "path/to/new_model.obj"`
