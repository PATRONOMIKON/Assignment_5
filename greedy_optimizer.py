"""
Greedy Algorithms Assignment
Completed implementations for delivery optimization.
"""

import json
import time
import heapq
import os


# ============================================================================
# PART 1: PACKAGE PRIORITIZATION (Activity Selection)
# ============================================================================

def maximize_deliveries(time_windows):
    """Return delivery IDs for the maximum number of non-overlapping deliveries."""
    # Earliest finish time leaves as much room as possible for later deliveries.
    ordered = sorted(time_windows, key=lambda item: (item["end"], item["start"]))
    selected = []
    last_end = float("-inf")

    for delivery in ordered:
        if delivery["start"] >= last_end:
            selected.append(delivery["delivery_id"])
            last_end = delivery["end"]

    return selected


# ============================================================================
# PART 2: TRUCK LOADING (Fractional Knapsack)
# ============================================================================

def optimize_truck_load(packages, weight_limit):
    """
    Maximize priority value under a weight limit, allowing fractional packages.

    Returns total priority, total weight, and selected package fractions.
    """
    remaining = max(0.0, float(weight_limit))
    total_priority = 0.0
    total_weight = 0.0
    selected = []

    # Ignore zero/negative weights because a value-per-weight ratio is undefined
    # for zero weight and negative weights are not meaningful for this problem.
    eligible = [
        package for package in packages
        if float(package["weight"]) > 0 and float(package["priority"]) > 0
    ]
    ordered = sorted(
        eligible,
        key=lambda package: float(package["priority"]) / float(package["weight"]),
        reverse=True,
    )

    for package in ordered:
        if remaining <= 0:
            break

        weight = float(package["weight"])
        priority = float(package["priority"])
        fraction = min(1.0, remaining / weight)
        if fraction <= 0:
            continue

        used_weight = weight * fraction
        gained_priority = priority * fraction
        selected.append({
            "package_id": package["package_id"],
            "fraction": fraction,
        })
        total_weight += used_weight
        total_priority += gained_priority
        remaining -= used_weight

    return {
        "total_priority": total_priority,
        "total_weight": total_weight,
        "packages": selected,
    }


# ============================================================================
# PART 3: DRIVER ASSIGNMENT (Interval Partitioning)
# ============================================================================

def minimize_drivers(deliveries):
    """
    Assign deliveries to the minimum number of drivers.

    Deliveries are processed by start time. A min-heap tracks each driver's
    next available time; the driver who becomes available earliest is reused
    whenever possible.
    """
    ordered = sorted(deliveries, key=lambda item: (item["start"], item["end"]))
    assignments = []
    # Heap entries: (driver's latest assigned delivery end time, driver index)
    available = []

    for delivery in ordered:
        start = delivery["start"]
        end = delivery["end"]

        if available and available[0][0] <= start:
            _, driver_index = heapq.heappop(available)
        else:
            driver_index = len(assignments)
            assignments.append([])

        assignments[driver_index].append(delivery["delivery_id"])
        heapq.heappush(available, (end, driver_index))

    return {
        "num_drivers": len(assignments),
        "assignments": assignments,
    }


# ============================================================================
# TESTING & BENCHMARKING
# ============================================================================

def load_scenario(filename):
    """Load a scenario from the scenarios directory."""
    with open(f"scenarios/{filename}", "r", encoding="utf-8") as file:
        return json.load(file)


def test_package_prioritization():
    """Test activity selection with known cases."""
    test1 = [
        {"delivery_id": "A", "start": 1, "end": 2},
        {"delivery_id": "B", "start": 3, "end": 4},
        {"delivery_id": "C", "start": 5, "end": 6},
    ]
    assert len(maximize_deliveries(test1)) == 3

    test2 = [
        {"delivery_id": "A", "start": 1, "end": 5},
        {"delivery_id": "B", "start": 2, "end": 4},
        {"delivery_id": "C", "start": 3, "end": 6},
    ]
    assert maximize_deliveries(test2) == ["B"]

    test3 = [
        {"delivery_id": "A", "start": 1, "end": 3},
        {"delivery_id": "B", "start": 2, "end": 5},
        {"delivery_id": "C", "start": 4, "end": 7},
        {"delivery_id": "D", "start": 6, "end": 9},
    ]
    assert len(maximize_deliveries(test3)) == 2
    print("Package prioritization: PASS")


def test_truck_loading():
    """Test fractional knapsack with known cases."""
    packages1 = [
        {"package_id": "A", "weight": 10, "priority": 60},
        {"package_id": "B", "weight": 20, "priority": 100},
    ]
    result1 = optimize_truck_load(packages1, 50)
    assert abs(result1["total_priority"] - 160) < 1e-9
    assert abs(result1["total_weight"] - 30) < 1e-9

    packages2 = [
        {"package_id": "A", "weight": 10, "priority": 60},
        {"package_id": "B", "weight": 20, "priority": 100},
        {"package_id": "C", "weight": 30, "priority": 120},
    ]
    result2 = optimize_truck_load(packages2, 50)
    assert abs(result2["total_priority"] - 240) < 1e-9
    assert abs(result2["total_weight"] - 50) < 1e-9
    print("Truck loading: PASS")


def test_driver_assignment():
    """Test interval partitioning with known cases."""
    deliveries1 = [
        {"delivery_id": "A", "start": 1, "end": 2},
        {"delivery_id": "B", "start": 3, "end": 4},
        {"delivery_id": "C", "start": 5, "end": 6},
    ]
    result1 = minimize_drivers(deliveries1)
    assert result1["num_drivers"] == 1

    deliveries2 = [
        {"delivery_id": "A", "start": 1, "end": 5},
        {"delivery_id": "B", "start": 2, "end": 6},
        {"delivery_id": "C", "start": 3, "end": 7},
    ]
    result2 = minimize_drivers(deliveries2)
    assert result2["num_drivers"] == 3

    deliveries3 = [
        {"delivery_id": "A", "start": 1, "end": 3},
        {"delivery_id": "B", "start": 2, "end": 4},
        {"delivery_id": "C", "start": 4, "end": 6},
        {"delivery_id": "D", "start": 5, "end": 7},
    ]
    result3 = minimize_drivers(deliveries3)
    assert result3["num_drivers"] == 2
    print("Driver assignment: PASS")


def benchmark_scenarios():
    """Benchmark all algorithms on generated scenario JSON files."""
    print("\\nBENCHMARKS")
    data = load_scenario("package_prioritization.json")
    start = time.perf_counter()
    result = maximize_deliveries(data)
    elapsed = time.perf_counter() - start
    print(f"Package prioritization: {len(result)}/{len(data)} deliveries, {elapsed * 1000:.4f} ms")

    data = load_scenario("truck_loading.json")
    start = time.perf_counter()
    result = optimize_truck_load(data["packages"], data["truck_capacity"])
    elapsed = time.perf_counter() - start
    print(
        f"Truck loading: priority {result['total_priority']:.2f}, "
        f"weight {result['total_weight']:.2f}, "
        f"{len(result['packages'])} packages/fractions, {elapsed * 1000:.4f} ms"
    )

    data = load_scenario("driver_assignment.json")
    start = time.perf_counter()
    result = minimize_drivers(data)
    elapsed = time.perf_counter() - start
    print(f"Driver assignment: {result['num_drivers']} drivers, {elapsed * 1000:.4f} ms")


if __name__ == "__main__":
    print("GREEDY ALGORITHMS ASSIGNMENT")
    test_package_prioritization()
    test_truck_loading()
    test_driver_assignment()
    # Generate scenarios with `python delivery_generator.py` before benchmarking.
    if os.path.isdir("scenarios") and all(
        os.path.exists(os.path.join("scenarios", name))
        for name in (
            "package_prioritization.json",
            "truck_loading.json",
            "driver_assignment.json",
        )
    ):
        benchmark_scenarios()
    else:
        print("Scenarios not found; run `python delivery_generator.py` to benchmark.")
