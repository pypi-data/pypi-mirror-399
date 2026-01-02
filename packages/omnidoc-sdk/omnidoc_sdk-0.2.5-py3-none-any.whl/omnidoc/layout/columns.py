def reorder_by_columns(blocks):
    blocks.sort(key=lambda b: (b.block.x_1, b.block.y_1))
    return blocks
