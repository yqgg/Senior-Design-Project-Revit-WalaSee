import ifcopenshell
import os
from datetime import datetime

# -------- Input Wall and Pipe Parameters
length_cm = 500  # Wall length in cm
height_cm = 300  # Wall height in cm
thickness_cm = 20  # Wall thickness in cm

pipe_radius_cm = 5   # Pipe radius in cm
custom_pipe_positions = [
    (50, 25, 50),  # (x, y, z) in centimeters
    (150, 25, 100),
    (300, 25, 150)
]

# -------- Convert to meters
length = length_cm / 100.0
height = height_cm / 100.0
thickness = thickness_cm / 100.0
pipe_radius = pipe_radius_cm / 100.0
custom_pipe_positions = [(x/100.0, y/100.0, z/100.0) for x, y, z in custom_pipe_positions]

# -------- Create IFC Model
model = ifcopenshell.file(schema="IFC4")

# -------- Project Structure
project = model.create_entity("IfcProject", GlobalId="0RANDOMGUID01", Name="WallWithPipesProject")
site = model.create_entity("IfcSite", GlobalId="0RANDOMGUID02", Name="Site")
building = model.create_entity("IfcBuilding", GlobalId="0RANDOMGUID03", Name="Building")
storey = model.create_entity("IfcBuildingStorey", GlobalId="0RANDOMGUID04", Name="Floor 1")

model.create_entity("IfcRelAggregates", GlobalId="rel01", RelatingObject=project, RelatedObjects=[site])
model.create_entity("IfcRelAggregates", GlobalId="rel02", RelatingObject=site, RelatedObjects=[building])
model.create_entity("IfcRelAggregates", GlobalId="rel03", RelatingObject=building, RelatedObjects=[storey])

# -------- Wall
wall = model.create_entity("IfcWallStandardCase", GlobalId="WALLGUID1234", Name="SimpleWall")

model.create_entity(
    "IfcRelContainedInSpatialStructure",
    GlobalId="rel04",
    RelatingStructure=storey,
    RelatedElements=[wall]
)

wall.ObjectPlacement = model.create_entity(
    "IfcLocalPlacement",
    PlacementRelTo=None,
    RelativePlacement=model.create_entity(
        "IfcAxis2Placement3D",
        Location=model.create_entity("IfcCartesianPoint", Coordinates=[0.0, 0.0, 0.0]),
        Axis=model.create_entity("IfcDirection", DirectionRatios=[0.0, 0.0, 1.0]),
        RefDirection=model.create_entity("IfcDirection", DirectionRatios=[1.0, 0.0, 0.0])
    )
)

wall_profile = model.create_entity(
    "IfcArbitraryClosedProfileDef",
    ProfileType="AREA",
    OuterCurve=model.create_entity(
        "IfcPolyline",
        Points=[
            model.create_entity("IfcCartesianPoint", Coordinates=[0.0, 0.0, 0.0]),
            model.create_entity("IfcCartesianPoint", Coordinates=[length, 0.0, 0.0]),
            model.create_entity("IfcCartesianPoint", Coordinates=[length, thickness, 0.0]),
            model.create_entity("IfcCartesianPoint", Coordinates=[0.0, thickness, 0.0]),
            model.create_entity("IfcCartesianPoint", Coordinates=[0.0, 0.0, 0.0]),
        ]
    )
)

wall_solid = model.create_entity(
    "IfcExtrudedAreaSolid",
    SweptArea=wall_profile,
    Position=model.create_entity(
        "IfcAxis2Placement3D",
        Location=model.create_entity("IfcCartesianPoint", Coordinates=[0.0, 0.0, 0.0]),
        Axis=model.create_entity("IfcDirection", DirectionRatios=[0.0, 0.0, 1.0]),
        RefDirection=model.create_entity("IfcDirection", DirectionRatios=[1.0, 0.0, 0.0])
    ),
    ExtrudedDirection=model.create_entity("IfcDirection", DirectionRatios=[0.0, 0.0, 1.0]),
    Depth=height
)

context = model.create_entity(
    "IfcGeometricRepresentationContext",
    ContextIdentifier="Body",
    ContextType="Model",
    CoordinateSpaceDimension=3,
    Precision=1.0e-5,
    WorldCoordinateSystem=model.create_entity(
        "IfcAxis2Placement3D",
        Location=model.create_entity("IfcCartesianPoint", Coordinates=[0.0, 0.0, 0.0])
    )
)

wall_shape = model.create_entity(
    "IfcShapeRepresentation",
    ContextOfItems=context,
    RepresentationIdentifier="Body",
    RepresentationType="SweptSolid",
    Items=[wall_solid]
)

wall.Representation = model.create_entity(
    "IfcProductDefinitionShape",
    Representations=[wall_shape]
)

# -------- Pipes at Custom Positions
pipe_counter = 0

for (x, y, z) in custom_pipe_positions:
    pipe = model.create_entity("IfcPipeSegment", GlobalId=f"PIPEGUID{pipe_counter:04d}", Name=f"Pipe{pipe_counter}")

    model.create_entity(
        "IfcRelContainedInSpatialStructure",
        GlobalId=f"relPipe{pipe_counter:04d}",
        RelatingStructure=storey,
        RelatedElements=[pipe]
    )

    pipe.ObjectPlacement = model.create_entity(
        "IfcLocalPlacement",
        PlacementRelTo=None,
        RelativePlacement=model.create_entity(
            "IfcAxis2Placement3D",
            Location=model.create_entity("IfcCartesianPoint", Coordinates=[x, y, z]),
            Axis=model.create_entity("IfcDirection", DirectionRatios=[0.0, 0.0, 1.0]),
            RefDirection=model.create_entity("IfcDirection", DirectionRatios=[1.0, 0.0, 0.0])
        )
    )

    pipe_profile = model.create_entity(
        "IfcCircleProfileDef",
        ProfileType="AREA",
        Radius=pipe_radius
    )

    pipe_solid = model.create_entity(
        "IfcExtrudedAreaSolid",
        SweptArea=pipe_profile,
        Position=model.create_entity(
            "IfcAxis2Placement3D",
            Location=model.create_entity("IfcCartesianPoint", Coordinates=[0.0, 0.0, 0.0]),
            Axis=model.create_entity("IfcDirection", DirectionRatios=[0.0, 0.0, 1.0]),
            RefDirection=model.create_entity("IfcDirection", DirectionRatios=[1.0, 0.0, 0.0])
        ),
        ExtrudedDirection=model.create_entity("IfcDirection", DirectionRatios=[0.0, 0.0, 1.0]),
        Depth=height - z
    )

    pipe_shape = model.create_entity(
        "IfcShapeRepresentation",
        ContextOfItems=context,
        RepresentationIdentifier="Body",
        RepresentationType="SweptSolid",
        Items=[pipe_solid]
    )

    pipe.Representation = model.create_entity(
        "IfcProductDefinitionShape",
        Representations=[pipe_shape]
    )

    pipe_counter += 1

# -------- Export IFC
output_dir = "ifc_outputs"
os.makedirs(output_dir, exist_ok=True)
timestamp_for_file = datetime.now().strftime("%m%d%y_%H%M")
output_file = os.path.join(output_dir, f"wall_with_pipes_{timestamp_for_file}.ifc")
model.write(output_file)

print(f"IFC file created and saved as: {output_file}")
