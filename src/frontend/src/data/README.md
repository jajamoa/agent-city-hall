# SF Zoning Grid Configuration

This document explains the structure of the `sfZoningGrid.json` file.

## Grid Configuration

- `cellSize`: Size of each grid cell in meters (100m)
- `bounds`: Geographic boundaries of the grid
  - `north`: Northern latitude boundary (37.8120)
  - `south`: Southern latitude boundary (37.7080)
  - `east`: Eastern longitude boundary (-122.3549)
  - `west`: Western longitude boundary (-122.5157)

## Height Limits

- `default`: Default height limit in feet (40ft)
- `options`: Available height limit options in feet [40, 65, 80, 85, 105, 130, 140, 240, 300]

## Cells

Grid cells are stored using a sparse matrix approach, where only modified cells are stored.
The key format is "row_col" (e.g., "10_15").

Each cell contains:
- `heightLimit`: Height limit in feet
- `category`: Land use category (e.g., "residential", "mixed_use")
- `lastUpdated`: Date of last update (YYYY-MM-DD format) 