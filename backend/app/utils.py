# Calculate MTTR (Mean Time To Repair)
def calculate_mttr(start, end):
    return (end - start).total_seconds()