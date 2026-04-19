# White Paper: The Architecture of Modern Graphics Processing Units (GPUs)

## Abstract
This white paper explores the architectural evolution and fundamental design principles of modern Graphics Processing Units (GPUs). Originally designed for rendering graphics, GPUs have transformed into highly parallel, general-purpose computing engines that power today's most demanding workloads, from scientific simulations to artificial intelligence.

## 1. Evolution of Parallel Processing
The origins of the GPU trace back to specialized electronic circuits designed exclusively for digital image processing and accelerating computer graphics. Early graphics controllers, such as video display controllers or blitters, lacked internal calculation capabilities and were restricted to basic memory movement. 

During the 1990s and 2000s, the modern GPU emerged. These processors gained the ability to perform operations like drawing lines and text independently of the Central Processing Unit (CPU), eventually incorporating 3D functionality and custom programmable shaders. Because graphics functions—such as calculating pixel colors—are inherently independent, they lend themselves perfectly to parallel calculation engines. 

This parallel nature gave rise to General-Purpose computing on GPUs (GPGPU). By the early 21st century, GPGPU pipelines allowed CPUs to offload embarrassingly parallel problems to GPUs. The theoretical speedup of such parallelization can be modeled by Amdahl's Law:
$$ S_{\text{latency}}(s) = \frac{1}{(1-p) + \frac{p}{s}} $$
where $S_{\text{latency}}$ is the theoretical speedup, $p$ is the proportion of execution time that benefits from parallelization, and $s$ is the speedup of the parallelized part. As $s \to \infty$, the maximum speedup is bounded by $\frac{1}{1-p}$. GPUs maximize $s$ by deploying thousands of calculation units, revolutionizing scientific computing and dominating the TOP500 supercomputer list.

## 2. Streaming Multiprocessors and Core Design
The fundamental processing unit within a modern GPU is the Streaming Multiprocessor (SM). A GPU consists of multiple SMs, each containing numerous processing cores, registers, and shared memory. 

Workloads are divided into threads, which are grouped into "thread blocks" (typically up to 1024 threads per block in modern architectures). All threads within the same thread block run concurrently on the same SM. This hierarchy allows threads within a block to communicate efficiently via shared memory, barrier synchronization, and atomic operations. 

Multiple thread blocks are combined to form a "grid," allowing computations to scale seamlessly across all available multiprocessors on the GPU. The global thread ID in a 1D grid can be calculated as:
$$ i = \text{blockIdx.x} \times \text{blockDim.x} + \text{threadIdx.x} $$

Core designs have evolved significantly from simple shading units. Modern SMs include standard cores (e.g., CUDA cores) for general parallel tasks, as well as specialized cores designed for specific workloads, such as ray tracing cores and Tensor Cores.

## 3. Memory Hierarchy and Bandwidth
To feed thousands of cores simultaneously, GPUs require massive memory bandwidth. The memory hierarchy of a GPU typically consists of fast, on-chip shared memory/L1 cache per SM, a unified L2 cache, and high-capacity off-chip global memory.

The theoretical memory bandwidth $B$ (in GB/s) can be calculated using the formula:
$$ B = \frac{f_{\text{mem}} \times W_{\text{bus}} \times D}{8 \times 10^9} $$
where $f_{\text{mem}}$ is the memory clock frequency (in Hz), $W_{\text{bus}}$ is the memory bus width (in bits), and $D$ is the data rate multiplier (e.g., 2 for Double Data Rate).

To meet these high bandwidth requirements, GPUs utilize specialized memory technologies:
*   **GDDR SDRAM:** Graphics Double Data Rate SDRAM is block-accessible and optimized for high bandwidth, unlike standard byte-accessible DDR SDRAM. Generations have evolved from the original GDDR to GDDR6X and the upcoming GDDR7.
*   **High Bandwidth Memory (HBM):** Introduced in 2013, HBM uses a 3D-stacked SDRAM interface connected via a silicon interposer. It provides massive bandwidth and power efficiency, making it the standard for high-performance datacenter GPUs and AI accelerators. The progression from HBM to HBM3 (and HBM4 expected in 2025) has been critical in supporting the exponential growth of AI models.

## 4. The SIMT Execution Model
Modern GPUs employ the Single Instruction, Multiple Threads (SIMT) execution model. In SIMT, a single central control unit broadcasts an instruction to multiple processing units (PUs). All PUs optionally perform simultaneous, synchronous, and fully-independent parallel execution of that single instruction.

Unlike multi-core CPUs (MIMD - Multiple Instruction, Multiple Data), where each core has its own instruction cache, decoder, and program counter, SIMT cores share a single instruction cache and decoder. Each PU maintains its own independent data, address registers, and memory, but relies on the central control unit for the program counter.

A critical challenge in the SIMT model is **branch divergence**. Because instructions are broadcast synchronously, threads within a warp (a sub-group of a thread block, typically 32 threads) cannot easily diverge. If threads take different paths in a conditional branch (e.g., an `if-else` statement), the execution paths must be serialized. The total execution time $T_{\text{warp}}$ for a divergent branch becomes the sum of the execution times of the taken paths:
$$ T_{\text{warp}} = T_{\text{if\_path}} + T_{\text{else\_path}} $$
This serialization significantly reduces computational efficiency, making branch minimization a key optimization strategy in GPU programming.

## 5. AI Acceleration and Future Trends
GPUs have become the dominant hardware for Artificial Intelligence (AI) and Machine Learning (ML). Neural networks rely heavily on linear algebra, particularly matrix multiplications, which GPUs accelerate natively. The core operation in deep learning is the General Matrix Multiply (GEMM):
$$ C = \alpha A B + \beta C $$
where $A$, $B$, and $C$ are matrices. 

To accelerate these operations, Nvidia introduced **Tensor Cores** in the Volta microarchitecture (2017). Tensor Cores are specialized hardware units designed to perform mixed-precision matrix math in a single clock cycle, delivering throughput far beyond that of regular CUDA cores.

The industry is also seeing the rise of **Neural Processing Units (NPUs)** and AI accelerators, which focus on low-precision arithmetic (e.g., INT8, FP8), novel dataflow architectures, and in-memory computing. 

**Future Trends:**
*   **Datacenter to Consumer:** While datacenter chips like the Nvidia H100 contain tens of billions of transistors, AI acceleration is rapidly moving to consumer devices. NPUs and Versatile Processor Units (VPUs) are now integrated into smartphone chips (Apple Silicon, Google Tensor) and PC processors (Intel Meteor Lake, AMD AI engines).
*   **AI in Graphics:** Technologies like Nvidia's Deep Learning Super Sampling (DLSS) leverage AI and Tensor Cores to upscale lower-resolution renders in real-time, significantly boosting frame rates.
*   **Scaling and Spatial Computing:** Future architectures will feature continued integration of AI-specific hardware, massive scaling of HBM capacities, and spatial computing designs to handle the exponential growth in AI model sizes and complexity.