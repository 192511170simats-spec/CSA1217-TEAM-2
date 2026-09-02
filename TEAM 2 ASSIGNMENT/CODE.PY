import random
import time


# ============================================================
# PROPOSED OPTIMIZED COMPUTER ARCHITECTURE SIMULATOR
# ============================================================

class ProcessorConfig:
    def __init__(self):
        self.cpu_cores = 4
        self.clock_ghz = 3.6

        # Cache configuration
        self.l1_size = 64
        self.l2_size = 512
        self.l3_size = 2048

        # Cache hit rates
        self.l1_hit_rate = 0.80
        self.l2_hit_rate = 0.12
        self.l3_hit_rate = 0.05

        # DMA configuration
        self.dma_channels = 4
        self.dma_bandwidth_mb = 1200

        # Pipeline
        self.pipeline_stages = 5
        self.branch_prediction_accuracy = 0.92

        # Workload
        self.total_blocks = 20
        self.data_per_block_kb = 256


class Cache:
    def __init__(self, name, hit_rate, hit_time):
        self.name = name
        self.hit_rate = hit_rate
        self.hit_time = hit_time

        self.accesses = 0
        self.hits = 0
        self.misses = 0

    def access(self):
        self.accesses += 1

        if random.random() < self.hit_rate:
            self.hits += 1
            return True

        self.misses += 1
        return False

    def hit_percentage(self):
        if self.accesses == 0:
            return 0

        return (self.hits / self.accesses) * 100


class CPUCore:
    def __init__(self, core_id):
        self.core_id = core_id

        self.instructions = 0
        self.cycles = 0
        self.stalls = 0

        self.vector_operations = 0
        self.branch_predictions = 0
        self.correct_predictions = 0

    def execute_normal(self, instructions):
        self.instructions += instructions

        # Normal instructions require approximately 1 cycle
        self.cycles += instructions

    def execute_vector(self, elements):
        self.vector_operations += 1

        # Vector unit processes multiple elements together
        vector_width = 8

        instruction_count = max(1, elements // vector_width)

        self.instructions += instruction_count
        self.cycles += instruction_count

    def branch_prediction(self, branches):
        self.branch_predictions += branches

        correct = 0

        for _ in range(branches):
            if random.random() < 0.92:
                correct += 1

        self.correct_predictions += correct

        incorrect = branches - correct

        # Each wrong prediction creates pipeline stalls
        penalty = 4

        self.stalls += incorrect * penalty
        self.cycles += incorrect * penalty


class DMAController:
    def __init__(self, channels, bandwidth):
        self.channels = channels
        self.bandwidth = bandwidth

        self.transfers = 0
        self.total_data_mb = 0
        self.transfer_time = 0

    def transfer(self, size_kb):
        self.transfers += 1

        size_mb = size_kb / 1024

        self.total_data_mb += size_mb

        # Time = Data / Bandwidth
        transfer_time = size_mb / self.bandwidth

        self.transfer_time += transfer_time

        return transfer_time


class WorkloadBlock:
    def __init__(self, block_id, data_size_kb):
        self.block_id = block_id
        self.data_size_kb = data_size_kb

        self.instructions = random.randint(8000, 15000)
        self.vector_elements = random.randint(500, 2000)
        self.branches = random.randint(100, 400)

        self.cache_hit = False
        self.dma_required = False


# ============================================================
# PROCESSOR SIMULATOR
# ============================================================

class ProcessorSimulator:

    def __init__(self):
        self.config = ProcessorConfig()

        # CPU cores
        self.cores = [
            CPUCore(i)
            for i in range(self.config.cpu_cores)
        ]

        # Cache hierarchy
        self.l1_cache = Cache(
            "L1 Cache",
            self.config.l1_hit_rate,
            1
        )

        self.l2_cache = Cache(
            "L2 Cache",
            self.config.l2_hit_rate,
            5
        )

        self.l3_cache = Cache(
            "L3 Cache",
            self.config.l3_hit_rate,
            15
        )

        # DMA
        self.dma = DMAController(
            self.config.dma_channels,
            self.config.dma_bandwidth_mb
        )

        self.total_execution_time = 0

        self.pipeline_stalls = 0
        self.memory_transfers = 0

        self.prefetch_operations = 0

        self.output_buffer = []

    # --------------------------------------------------------
    # PREFETCH
    # --------------------------------------------------------

    def prefetch(self, block):

        # Frequently accessed data is prefetched
        if random.random() < 0.70:
            self.prefetch_operations += 1
            return True

        return False

    # --------------------------------------------------------
    # CACHE ACCESS
    # --------------------------------------------------------

    def access_cache(self):

        # Check L1
        if self.l1_cache.access():
            return "L1"

        # L1 miss -> L2
        if self.l2_cache.access():
            return "L2"

        # L2 miss -> L3
        if self.l3_cache.access():
            return "L3"

        # Complete cache miss
        return "MEMORY"

    # --------------------------------------------------------
    # PROCESS ONE WORKLOAD BLOCK
    # --------------------------------------------------------

    def process_block(self, block, core):

        print(
            f"\nCore {core.core_id} processing Block {block.block_id}"
        )

        # ----------------------------------------------------
        # Step 1: Prefetch
        # ----------------------------------------------------

        prefetched = self.prefetch(block)

        if prefetched:
            print("  Data prefetch: Successful")

        else:
            print("  Data prefetch: Not required")

        # ----------------------------------------------------
        # Step 2: Cache lookup
        # ----------------------------------------------------

        cache_level = self.access_cache()

        print(
            f"  Data location: {cache_level}"
        )

        # ----------------------------------------------------
        # Step 3: Execute based on cache result
        # ----------------------------------------------------

        if cache_level != "MEMORY":

            block.cache_hit = True

            print("  Cache hit -> CPU execution")

            # Normal CPU operations
            core.execute_normal(block.instructions)

            # Vector processing
            core.execute_vector(block.vector_elements)

        else:

            block.cache_hit = False
            block.dma_required = True

            print(
                "  Cache miss -> DMA/Memory transfer initiated"
            )

            # DMA transfer
            dma_time = self.dma.transfer(
                block.data_size_kb
            )

            self.memory_transfers += 1

            # CPU continues independent instructions
            independent_instructions = int(
                block.instructions * 0.30
            )

            core.execute_normal(
                independent_instructions
            )

            # Memory waiting causes some stalls
            memory_stall = 10

            core.stalls += memory_stall
            core.cycles += memory_stall

            # Vector processing after data arrival
            core.execute_vector(
                block.vector_elements
            )

            self.total_execution_time += dma_time

        # ----------------------------------------------------
        # Step 4: Branch prediction
        # ----------------------------------------------------

        core.branch_prediction(
            block.branches
        )

        # ----------------------------------------------------
        # Step 5: Store results
        # ----------------------------------------------------

        result = {
            "block": block.block_id,
            "core": core.core_id,
            "cache": cache_level,
            "instructions": block.instructions
        }

        self.output_buffer.append(result)

        print(
            f"  Instructions: {block.instructions}"
        )

        print(
            f"  Pipeline stalls: {core.stalls}"
        )

        print("  Block completed.")

    # --------------------------------------------------------
    # RUN COMPLETE WORKLOAD
    # --------------------------------------------------------

    def run(self):

        print("=" * 65)
        print(" PROPOSED OPTIMIZED COMPUTER ARCHITECTURE SIMULATION")
        print("=" * 65)

        print("\nInitializing system...")

        print(
            f"CPU Cores       : {self.config.cpu_cores}"
        )

        print(
            f"Clock Speed     : {self.config.clock_ghz} GHz"
        )

        print(
            f"Pipeline Stages : {self.config.pipeline_stages}"
        )

        print(
            f"DMA Channels    : {self.config.dma_channels}"
        )

        print(
            f"Workload Blocks : {self.config.total_blocks}"
        )

        print("\nSystem initialization completed.")

        # ----------------------------------------------------
        # Create workload
        # ----------------------------------------------------

        workload = []

        for i in range(1, self.config.total_blocks + 1):

            block = WorkloadBlock(
                i,
                self.config.data_per_block_kb
            )

            workload.append(block)

        # ----------------------------------------------------
        # Divide workload among CPU cores
        # ----------------------------------------------------

        print("\nDividing workload among CPU cores...")

        start_time = time.perf_counter()

        for index, block in enumerate(workload):

            core = self.cores[
                index % self.config.cpu_cores
            ]

            self.process_block(
                block,
                core
            )

        # ----------------------------------------------------
        # Transfer completed output using DMA
        # ----------------------------------------------------

        print("\nTransferring completed output using DMA...")

        output_size = len(
            self.output_buffer
        ) * 4

        self.dma.transfer(
            output_size
        )

        self.memory_transfers += 1

        end_time = time.perf_counter()

        real_execution_time = (
            end_time - start_time
        )

        # ----------------------------------------------------
        # Calculate metrics
        # ----------------------------------------------------

        self.calculate_metrics(
            real_execution_time
        )

    # --------------------------------------------------------
    # PERFORMANCE ANALYSIS
    # --------------------------------------------------------

    def calculate_metrics(self, real_time):

        print("\n")
        print("=" * 65)
        print(" PERFORMANCE ANALYSIS")
        print("=" * 65)

        total_instructions = 0
        total_cycles = 0
        total_stalls = 0
        total_branches = 0
        correct_branches = 0

        for core in self.cores:

            total_instructions += core.instructions
            total_cycles += core.cycles
            total_stalls += core.stalls

            total_branches += (
                core.branch_predictions
            )

            correct_branches += (
                core.correct_predictions
            )

        # CPI
        if total_instructions > 0:

            cpi = (
                total_cycles /
                total_instructions
            )

        else:

            cpi = 0

        # CPU execution time
        clock_frequency = (
            self.config.clock_ghz * 1_000_000_000
        )

        cpu_time = (
            total_cycles /
            clock_frequency
        )

        # Cache statistics
        l1_hit = self.l1_cache.hit_percentage()
        l2_hit = self.l2_cache.hit_percentage()
        l3_hit = self.l3_cache.hit_percentage()

        # Branch prediction
        if total_branches > 0:

            prediction_accuracy = (
                correct_branches /
                total_branches
            ) * 100

        else:

            prediction_accuracy = 0

        # DMA throughput
        if self.dma.transfer_time > 0:

            throughput = (
                self.dma.total_data_mb /
                self.dma.transfer_time
            )

        else:

            throughput = 0

        # ----------------------------------------------------
        # Display results
        # ----------------------------------------------------

        print(
            f"\nTotal Instructions       : "
            f"{total_instructions:,}"
        )

        print(
            f"Total Clock Cycles      : "
            f"{total_cycles:,}"
        )

        print(
            f"Average CPI             : "
            f"{cpi:.3f}"
        )

        print(
            f"CPU Execution Time      : "
            f"{cpu_time:.6f} seconds"
        )

        print(
            f"Pipeline Stall Cycles   : "
            f"{total_stalls:,}"
        )

        print(
            f"L1 Cache Hit Rate       : "
            f"{l1_hit:.2f}%"
        )

        print(
            f"L2 Cache Hit Rate       : "
            f"{l2_hit:.2f}%"
        )

        print(
            f"L3 Cache Hit Rate       : "
            f"{l3_hit:.2f}%"
        )

        print(
            f"Branch Prediction       : "
            f"{prediction_accuracy:.2f}%"
        )

        print(
            f"DMA Transfers           : "
            f"{self.dma.transfers}"
        )

        print(
            f"DMA Data Transferred    : "
            f"{self.dma.total_data_mb:.2f} MB"
        )

        print(
            f"I/O Throughput          : "
            f"{throughput:.2f} MB/s"
        )

        print(
            f"Prefetch Operations     : "
            f"{self.prefetch_operations}"
        )

        # ----------------------------------------------------
        # Identify bottleneck
        # ----------------------------------------------------

        self.identify_bottleneck(
            total_stalls,
            l1_hit,
            throughput
        )

    # --------------------------------------------------------
    # BOTTLENECK IDENTIFICATION
    # --------------------------------------------------------

    def identify_bottleneck(
        self,
        stalls,
        l1_hit_rate,
        throughput
    ):

        print("\n")
        print("=" * 65)
        print(" BOTTLENECK ANALYSIS")
        print("=" * 65)

        problems = []

        if l1_hit_rate < 75:

            problems.append(
                "L1 cache miss rate is relatively high"
            )

        if stalls > 1000:

            problems.append(
                "Pipeline stalls are significant"
            )

        if throughput < 1000:

            problems.append(
                "I/O or DMA throughput may be a bottleneck"
            )

        if not problems:

            print(
                "\nNo major bottleneck detected."
            )

            print(
                "The proposed architecture is "
                "performing efficiently."
            )

        else:

            print("\nDominant bottlenecks:")

            for problem in problems:

                print(
                    f" - {problem}"
                )

        print("\nRecommended optimizations:")

        print(
            " - Increase cache capacity"
        )

        print(
            " - Improve data prefetching"
        )

        print(
            " - Improve branch prediction"
        )

        print(
            " - Increase DMA bandwidth"
        )

        print(
            " - Use more parallel CPU cores"
        )

        print(
            " - Reduce pipeline stalls"
        )

        print("\nSimulation completed.")


# ============================================================
# MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    simulator = ProcessorSimulator()

    simulator.run()
