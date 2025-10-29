# backend/populate_content.py
"""
Populate EduCore AI with comprehensive study materials
Run this script to add courses, lessons, resources, and quizzes
Usage: python manage.py shell < populate_content.py
"""

from learning.models import Course, Lesson, Resource, Quiz, Question
from django.contrib.auth import get_user_model
from django.utils import timezone
import os
import django
from datetime import timedelta
from django.db import transaction

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()


User = get_user_model()

print("🚀 Starting Comprehensive Content Population...")

# Get or create instructor
try:
    instructor = User.objects.get(username='instructor')
    print(f"Found instructor user")
except User.DoesNotExist:
    instructor = User.objects.create_user(
        username='instructor',
        email='instructor@educore.com',
        password='instructor123',
        first_name='John',
        last_name='Professor'
    )
    instructor.is_staff = True
    instructor.save()
    print(f"Created instructor user: instructor/instructor123")

# ========== OPERATING SYSTEMS 2 ==========
print("\n📚 Creating Operating Systems 2 Course...")

os2_course, created = Course.objects.get_or_create(
    title="Operating Systems 2",
    defaults={
        'description': '''Advanced operating system concepts including process management, memory management, file systems, and security. 
        This course covers modern OS architectures, concurrency, deadlocks, and real-world implementations.''',
        'instructor': instructor,
        'is_published': True,
        'difficulty': 'advanced'
    }
)

if created:
    print("Created Operating Systems 2 course")
else:
    print("Operating Systems 2 course exists")

# OS2 Lessons with comprehensive content
os2_lessons_data = [
    {
        'title': 'Chapter 1: Introduction to Advanced OS Concepts',
        'order': 1,
        'difficulty': 'intermediate',
        'estimated_time_minutes': 90,
        'content': '''
# Introduction to Advanced Operating Systems

## What is an Operating System?

An Operating System (OS) is system software that manages computer hardware and software resources and provides common services for computer programs. It acts as an intermediary between users and computer hardware.

### Key Functions of an OS:
1. **Process Management** - Creating, scheduling, and terminating processes
2. **Memory Management** - Allocating and deallocating memory space
3. **File System Management** - Managing files and directories
4. **Device Management** - Managing I/O devices
5. **Security and Protection** - Protecting resources from unauthorized access

## Operating System Types

### 1. Batch Operating Systems
- Jobs are batched together and executed without user interaction
- Efficient for repetitive tasks
- Examples: Early IBM systems

### 2. Time-Sharing Systems
- Multiple users share computing resources simultaneously
- CPU switches between processes rapidly (time slicing)
- Provides illusion of dedicated system for each user
- Examples: Unix, Linux

### 3. Distributed Systems
- Multiple interconnected computers working together
- Resources are shared across the network
- Examples: Google's infrastructure, Hadoop clusters

### 4. Real-Time Systems
- Processes must complete within strict time constraints
- Used in embedded systems, medical devices, aerospace
- Two types:
  - **Hard Real-Time**: Missing deadline causes system failure
  - **Soft Real-Time**: Missing deadline degrades performance

## Operating System Architecture

### Monolithic Kernel
- All OS services run in kernel space
- Fast performance due to direct function calls
- **Pros**: High performance, simple inter-module communication
- **Cons**: Less modular, bugs can crash entire system
- **Examples**: Traditional Unix, Linux kernel

### Microkernel
- Minimal kernel with basic services only
- Other services run in user space
- **Pros**: More stable, modular, easier to maintain
- **Cons**: Slower due to message passing overhead
- **Examples**: Minix, QNX, L4

### Hybrid Kernel
- Combination of monolithic and microkernel
- Some services in kernel, others in user space
- **Examples**: Windows NT, macOS (XNU kernel)

## System Calls

System calls are the interface between user programs and the OS kernel.

### Common System Call Categories:

1. **Process Control**
   - `fork()` - Create new process
   - `exec()` - Execute a program
   - `exit()` - Terminate process
   - `wait()` - Wait for child process

2. **File Management**
   - `open()` - Open file
   - `read()` - Read from file
   - `write()` - Write to file
   - `close()` - Close file

3. **Device Management**
   - `ioctl()` - Device-specific control operations
   - `read()`, `write()` - I/O operations

4. **Information Maintenance**
   - `getpid()` - Get process ID
   - `time()` - Get system time
   - `sleep()` - Delay process execution

5. **Communication**
   - `pipe()` - Create IPC pipe
   - `shmget()` - Get shared memory segment
   - `msgget()` - Get message queue

### System Call Execution Flow:

```
1. User program calls library function
2. Library function sets up system call number and parameters
3. Execute trap instruction (software interrupt)
4. CPU switches to kernel mode
5. Kernel handles the request
6. Return to user mode with result
```

## Interrupts and Exceptions

### Hardware Interrupts
- Asynchronous signals from hardware devices
- Examples: Keyboard input, disk I/O completion, timer
- Handled by interrupt service routines (ISRs)

### Software Interrupts (Traps)
- Intentional interrupts triggered by programs
- Used for system calls
- **Exception**: Error conditions like division by zero

### Interrupt Handling Process:
1. Device raises interrupt signal
2. CPU saves current state
3. CPU jumps to interrupt handler
4. Handler processes interrupt
5. CPU restores saved state and continues

## Boot Process

Understanding how an OS starts is crucial:

### 1. **BIOS/UEFI Stage**
- Power-on Self Test (POST)
- Initialize hardware
- Load boot loader from boot device

### 2. **Boot Loader Stage**
- GRUB (Linux) or NTLDR/BOOTMGR (Windows)
- Loads kernel into memory
- Passes control to kernel

### 3. **Kernel Initialization**
- Initialize memory management
- Set up process scheduler
- Mount root file system
- Start init/systemd process

### 4. **User Space Initialization**
- Init/systemd starts system services
- Start login manager
- System ready for users

## Modern OS Challenges

1. **Multicore Processing**
   - Efficient use of multiple CPU cores
   - Parallel algorithm design
   - Cache coherency

2. **Virtualization**
   - Running multiple OS instances on one physical machine
   - Hypervisors: Type 1 (bare-metal) vs Type 2 (hosted)

3. **Security**
   - Protecting against malware, exploits
   - Secure boot, kernel hardening
   - Sandboxing and isolation

4. **Energy Efficiency**
   - Power management in mobile devices
   - Dynamic voltage/frequency scaling
   - Sleep states (S0-S5)

## Performance Metrics

Key metrics for evaluating OS performance:

- **Throughput**: Number of processes completed per unit time
- **Response Time**: Time from request submission to first response
- **Turnaround Time**: Total time from submission to completion
- **CPU Utilization**: Percentage of time CPU is busy
- **Waiting Time**: Time process spends in ready queue

## Summary

Operating Systems are complex software that manage hardware resources and provide services to applications. Understanding OS architecture, system calls, interrupts, and modern challenges is essential for advanced study. In the following chapters, we'll dive deeper into process management, memory management, and file systems.

### Key Takeaways:
✓ OS acts as intermediary between hardware and applications
✓ Different OS types serve different purposes
✓ System calls provide controlled access to kernel services
✓ Interrupts enable efficient I/O handling
✓ Modern OSes face challenges in parallelism, virtualization, and security
        '''
    },
    {
        'title': 'Chapter 2: Process Management and Scheduling',
        'order': 2,
        'difficulty': 'advanced',
        'estimated_time_minutes': 120,
        'content': '''
# Process Management and CPU Scheduling

## What is a Process?

A **process** is a program in execution. It includes:
- **Program code** (text section)
- **Current activity** (program counter, register values)
- **Stack** (temporary data - function parameters, return addresses)
- **Data section** (global variables)
- **Heap** (dynamically allocated memory)

### Process vs Program
- **Program**: Passive entity (executable file on disk)
- **Process**: Active entity (program loaded in memory and executing)

## Process States

A process transitions through different states during execution:

### 1. **New**
- Process is being created
- Memory allocation, PCB initialization

### 2. **Ready**
- Process is waiting to be assigned to processor
- In ready queue

### 3. **Running**
- Instructions are being executed
- Only one process per CPU core can run at a time

### 4. **Waiting (Blocked)**
- Process is waiting for an event (I/O completion, signal)
- Cannot proceed until event occurs

### 5. **Terminated**
- Process has finished execution
- Resources are being deallocated

### State Transition Diagram:
```
New → Ready → Running → Terminated
         ↑       ↓
         ←  Waiting  ←
```

## Process Control Block (PCB)

The PCB is a data structure that contains all information about a process:

```c
struct process_control_block {
    int process_id;              // Unique process ID
    int process_state;           // Current state
    int program_counter;         // Address of next instruction
    int cpu_registers[16];       // Contents of CPU registers
    int cpu_scheduling_info;     // Priority, queue pointers
    int memory_management_info;  // Page tables, memory limits
    int accounting_info;         // CPU usage, time limits
    int io_status_info;          // List of open files, I/O devices
};
```

## Process Creation

### Fork-Exec Model (Unix/Linux)

**fork()** - Creates a new process (child) that is a copy of parent:

```c
#include <stdio.h>
#include <unistd.h>
#include <sys/types.h>

int main() {
    pid_t pid;
    
    pid = fork();  // Create child process
    
    if (pid < 0) {
        // Fork failed
        printf("Fork failed!\\n");
        return 1;
    }
    else if (pid == 0) {
        // Child process
        printf("Child process: PID = %d\\n", getpid());
        printf("Child's parent PID = %d\\n", getppid());
    }
    else {
        // Parent process
        printf("Parent process: PID = %d\\n", getpid());
        printf("Parent created child with PID = %d\\n", pid);
    }
    
    return 0;
}
```

**exec()** - Replaces current process with new program:

```c
#include <stdio.h>
#include <unistd.h>

int main() {
    pid_t pid = fork();
    
    if (pid == 0) {
        // Child process executes different program
        execl("/bin/ls", "ls", "-l", NULL);
        // Code below only runs if exec fails
        printf("Exec failed!\\n");
    }
    else {
        // Parent waits for child
        wait(NULL);
        printf("Child completed\\n");
    }
    
    return 0;
}
```

## CPU Scheduling

CPU scheduling determines which process runs when. Goals:
- **Maximize CPU utilization**
- **Maximize throughput**
- **Minimize response time**
- **Minimize waiting time**
- **Minimize turnaround time**

### Scheduling Algorithms

#### 1. First-Come, First-Served (FCFS)
- Processes execute in order of arrival
- **Non-preemptive**
- Simple but can cause convoy effect

**Example:**
```
Process    Arrival    Burst Time
P1         0          24
P2         1          3
P3         2          3

Gantt Chart: |P1(0-24)|P2(24-27)|P3(27-30)|

Average Waiting Time = (0 + 23 + 25) / 3 = 16ms
```

**Pros**: Simple to implement
**Cons**: Poor average waiting time, convoy effect

#### 2. Shortest Job First (SJF)
- Process with shortest burst time executes first
- **Non-preemptive** (Shortest Job First)
- **Preemptive** (Shortest Remaining Time First - SRTF)
- Optimal for minimum average waiting time

**Example:**
```
Process    Arrival    Burst Time
P1         0          7
P2         2          4
P3         4          1
P4         5          4

Non-preemptive SJF:
Gantt Chart: |P1(0-7)|P3(7-8)|P2(8-12)|P4(12-16)|

Average Waiting Time = (0 + 6 + 3 + 7) / 4 = 4ms
```

**Pros**: Optimal average waiting time
**Cons**: Difficult to predict burst time, starvation of long processes

#### 3. Priority Scheduling
- Each process has priority
- Higher priority processes execute first
- Can be preemptive or non-preemptive

**Problem**: Starvation - low priority processes may never execute
**Solution**: Aging - gradually increase priority of waiting processes

```c
// Priority scheduling with aging
void priority_schedule_with_aging() {
    while (processes_exist()) {
        // Age all waiting processes
        for (each waiting process p) {
            p.priority += aging_factor;
        }
        
        // Select highest priority process
        process* next = select_highest_priority();
        execute(next);
    }
}
```

#### 4. Round Robin (RR)
- Each process gets small time quantum (10-100ms)
- If process doesn't complete, goes to end of queue
- **Preemptive**
- Good for time-sharing systems

**Example with time quantum = 4ms:**
```
Process    Arrival    Burst Time
P1         0          24
P2         0          3
P3         0          3

Gantt Chart: |P1(0-4)|P2(4-7)|P3(7-10)|P1(10-14)|P1(14-18)|P1(18-22)|P1(22-26)|P1(26-30)|

Average Waiting Time = 17ms
```

**Time Quantum Selection:**
- Too large → Becomes FCFS
- Too small → Too much context switching overhead
- Typical: 10-100 milliseconds

#### 5. Multilevel Queue Scheduling
- Ready queue divided into separate queues
- Each queue has own scheduling algorithm
- Processes permanently assigned to queue

```
High Priority Queue:     |Interactive processes| → Round Robin (q=8ms)
Medium Priority Queue:   |I/O processes|        → SJF
Low Priority Queue:      |Batch processes|     → FCFS
```

## Process Synchronization

When multiple processes access shared data, we need synchronization to avoid **race conditions**.

### Critical Section Problem

A critical section is code where shared resources are accessed.

**Requirements for Solution:**
1. **Mutual Exclusion**: Only one process in critical section at a time
2. **Progress**: If no process in critical section, selection of next cannot be postponed indefinitely
3. **Bounded Waiting**: Limit on times other processes can enter while one is waiting

### Peterson's Solution (2 Processes)

```c
int turn;
bool flag[2];

// Process Pi
do {
    flag[i] = true;
    turn = j;
    while (flag[j] && turn == j)
        ;  // Busy wait
    
    /* CRITICAL SECTION */
    
    flag[i] = false;
    
    /* REMAINDER SECTION */
} while (true);
```

### Semaphores

A semaphore is an integer variable accessed through two atomic operations:

**wait(S)** or **P(S)**:
```c
wait(S) {
    while (S <= 0)
        ;  // Busy wait
    S--;
}
```

**signal(S)** or **V(S)**:
```c
signal(S) {
    S++;
}
```

**Binary Semaphore**: S ∈ {0, 1} (mutex)
**Counting Semaphore**: S can be any non-negative integer

### Classic Synchronization Problems

#### 1. Producer-Consumer Problem

```c
#define BUFFER_SIZE 10

int buffer[BUFFER_SIZE];
int in = 0, out = 0;

semaphore mutex = 1;        // Protects buffer access
semaphore empty = BUFFER_SIZE;  // Count of empty slots
semaphore full = 0;         // Count of full slots

// Producer
void producer() {
    int item;
    while (true) {
        item = produce_item();
        
        wait(empty);   // Wait for empty slot
        wait(mutex);   // Enter critical section
        
        buffer[in] = item;
        in = (in + 1) % BUFFER_SIZE;
        
        signal(mutex); // Leave critical section
        signal(full);  // Signal new full slot
    }
}

// Consumer
void consumer() {
    int item;
    while (true) {
        wait(full);    // Wait for full slot
        wait(mutex);   // Enter critical section
        
        item = buffer[out];
        out = (out + 1) % BUFFER_SIZE;
        
        signal(mutex); // Leave critical section
        signal(empty); // Signal new empty slot
        
        consume_item(item);
    }
}
```

#### 2. Readers-Writers Problem

```c
int read_count = 0;
semaphore mutex = 1;     // Protects read_count
semaphore wrt = 1;       // Controls writer access

// Reader
void reader() {
    wait(mutex);
    read_count++;
    if (read_count == 1)
        wait(wrt);       // First reader locks out writers
    signal(mutex);
    
    /* READING */
    
    wait(mutex);
    read_count--;
    if (read_count == 0)
        signal(wrt);     // Last reader unlocks for writers
    signal(mutex);
}

// Writer
void writer() {
    wait(wrt);
    
    /* WRITING */
    
    signal(wrt);
}
```

## Deadlocks

A set of processes is in **deadlock** if each process is waiting for an event that can only be caused by another process in the set.

### Necessary Conditions for Deadlock:
1. **Mutual Exclusion**: Resources cannot be shared
2. **Hold and Wait**: Process holds resources while waiting for others
3. **No Preemption**: Resources cannot be forcibly taken
4. **Circular Wait**: Circular chain of processes waiting for resources

### Deadlock Prevention

Break one of the four necessary conditions:

1. **Mutual Exclusion**: Make resources sharable (not always possible)
2. **Hold and Wait**: Require all resources at once
3. **No Preemption**: Allow resource preemption
4. **Circular Wait**: Impose ordering on resource types

### Banker's Algorithm (Deadlock Avoidance)

```c
// Check if system is in safe state
bool is_safe_state(int available[], int max[][], int allocation[][]) {
    int work[m];
    bool finish[n] = {false};
    
    for (int i = 0; i < m; i++)
        work[i] = available[i];
    
    // Find process that can finish
    while (true) {
        bool found = false;
        for (int i = 0; i < n; i++) {
            if (!finish[i] && can_allocate(i, work)) {
                // Process i can finish
                for (int j = 0; j < m; j++)
                    work[j] += allocation[i][j];
                finish[i] = true;
                found = true;
            }
        }
        if (!found) break;
    }
    
    // Check if all processes finished
    for (int i = 0; i < n; i++)
        if (!finish[i]) return false;
    return true;
}
```

## Summary

Process management is central to OS functionality. Key concepts:
- Processes have states and transitions
- PCB stores all process information
- CPU scheduling algorithms optimize different metrics
- Synchronization prevents race conditions
- Deadlocks must be prevented, avoided, or detected

### Key Takeaways:
✓ Understanding process lifecycle is crucial
✓ Different scheduling algorithms have different trade-offs
✓ Synchronization prevents race conditions
✓ Semaphores are powerful synchronization tools
✓ Deadlock prevention requires breaking necessary conditions
        '''
    },
    {
        'title': 'Chapter 3: Memory Management',
        'order': 3,
        'difficulty': 'advanced',
        'estimated_time_minutes': 120,
        'content': '''
# Memory Management

## Introduction

Memory management is crucial for efficient system operation. The OS must:
- Keep track of which parts of memory are in use
- Allocate memory to processes when needed
- Deallocate memory when processes finish
- Ensure protection between processes
- Provide virtual memory abstraction

## Address Binding

Programs must be loaded into memory to execute. Address binding determines when addresses are assigned.

### Types of Address Binding:

#### 1. Compile Time
- Absolute code generated
- If starting location changes, must recompile
- Example: MS-DOS .COM programs

#### 2. Load Time
- Relocatable code generated
- Final binding delayed until load time
- Code can be relocated in memory

#### 3. Execution Time
- Binding delayed until runtime
- Process can move during execution
- Requires hardware support (MMU)

## Logical vs Physical Address

- **Logical Address (Virtual Address)**: Generated by CPU, seen by program
- **Physical Address**: Actual location in memory
- **Memory Management Unit (MMU)**: Translates logical to physical addresses

### Simple Address Translation:
```
Physical Address = Logical Address + Base Register
```

## Memory Allocation

### Contiguous Allocation

#### Fixed Partitioning
- Memory divided into fixed-size partitions
- Each process assigned to one partition
- **Internal fragmentation**: Wasted space within partition

#### Dynamic Partitioning
- Partitions created dynamically
- Exact size needed for process
- **External fragmentation**: Wasted space between partitions

### Dynamic Allocation Strategies:

#### 1. First Fit
- Allocate first hole big enough
- Fast, but can create small holes at beginning

```python
def first_fit(process_size, memory_blocks):
    for i, block in enumerate(memory_blocks):
        if block.size >= process_size and block.free:
            allocate(block, process_size)
            return i
    return -1  # No fit found
```

#### 2. Best Fit
- Allocate smallest hole that fits
- Minimizes wasted space
- Can be slow (must search all holes)

```python
def best_fit(process_size, memory_blocks):
    best_idx = -1
    min_size = float('inf')
    
    for i, block in enumerate(memory_blocks):
        if block.free and block.size >= process_size:
            if block.size < min_size:
                min_size = block.size
                best_idx = i
    
    if best_idx != -1:
        allocate(memory_blocks[best_idx], process_size)
    return best_idx
```

#### 3. Worst Fit
- Allocate largest hole
- Leaves larger leftover holes
- Can be slow

### Fragmentation

**Internal Fragmentation**: Memory wasted within allocated region
**External Fragmentation**: Memory wasted between allocated regions

**Solution**: Compaction
- Shuffle memory contents to make free memory contiguous
- Only possible if relocation is dynamic
- Can be expensive

## Paging

Paging eliminates external fragmentation by breaking physical memory into fixed-size blocks.

### Key Concepts:

- **Page**: Fixed-size block of logical memory (typically 4KB)
- **Frame**: Fixed-size block of physical memory (same size as page)
- **Page Table**: Maps logical pages to physical frames

### Address Translation with Paging:

```
Logical Address = <Page Number, Page Offset>
```

**Example**: 32-bit logical address, 4KB pages
- Page size = 4KB = 2^12 bytes
- Page number = upper 20 bits
- Page offset = lower 12 bits

```
Logical Address:    |  Page Number (20 bits) | Offset (12 bits) |
                    ↓ Page Table Lookup
Physical Address:   | Frame Number (20 bits) | Offset (12 bits) |
```

### Page Table Structure:

```c
struct page_table_entry {
    unsigned int frame_number : 20;  // Physical frame number
    unsigned int present : 1;        // In memory?
    unsigned int dirty : 1;          // Modified?
    unsigned int accessed : 1;       // Recently used?
    unsigned int read_write : 1;     // Read/write permissions
    unsigned int user_supervisor : 1; // User/kernel mode
    unsigned int reserved : 7;       // Reserved bits
};
```

### Multi-Level Page Tables

Single-level page tables can be huge. Solution: Multiple levels.

**Two-Level Page Table Example:**

```
32-bit address space, 4KB pages:

Logical Address:
| Outer Page # (10 bits) | Inner Page # (10 bits) | Offset (12 bits) |

Translation:
1. Use outer page # to index outer page table → get inner page table
2. Use inner page # to index inner page table → get frame number
3. Combine frame number with offset → physical address
```

**Advantages:**
- Only need page tables for used address space
- Can be paged out themselves

### Inverted Page Tables

One entry for each physical frame instead of each logical page.

```c
struct inverted_page_table_entry {
    int process_id;
    unsigned int logical_page_number;
    // Other control bits
};
```

**Advantages**: Fixed size regardless of address space
**Disadvantages**: Slower lookups (must search entire table)

### Translation Lookaside Buffer (TLB)

Cache for page table entries to speed up address translation.

```
1. Check TLB for page number
2. If TLB hit: Get frame number directly
3. If TLB miss: 
   - Look up page table
   - Update TLB
   - Get frame number
```

**Performance:**
```
Effective Access Time = (TLB Hit Rate × TLB Access Time) + 
                       (TLB Miss Rate × Page Table Access Time)

Example:
TLB hit rate = 80%
TLB access = 1 ns
Memory access = 100 ns

EAT = 0.80 × 1 + 0.20 × 100 = 20.8 ns
```

## Segmentation

Segmentation divides logical address space into logical units (segments).

### Segments:
- Code segment
- Data segment
- Stack segment
- Heap segment

### Segment Table:

Each entry contains:
- **Base**: Starting physical address
- **Limit**: Length of segment

```
Logical Address = <Segment Number, Offset>

1. Check if offset < limit (protection)
2. Physical Address = base + offset
```

### Segmentation with Paging

Combine benefits of both:
- Segmentation: Logical view
- Paging: Physical memory management

**Intel x86 (Protected Mode)**: Uses segmentation and paging

## Virtual Memory

Virtual memory allows executing processes that are not completely in memory.

### Benefits:
- Programs can be larger than physical memory
- More processes in memory simultaneously
- Less I/O needed for swapping
- Easier programming (each process has own address space)

### Demand Paging

Pages loaded only when needed (on demand).

#### Page Fault Handling:

```
1. Reference to page not in memory → page fault
2. OS checks if reference is valid
3. If invalid → terminate process
4. If valid:
   a. Find free frame
   b. Swap page into frame from disk
   c. Update page table
   d. Restart instruction
```

#### Performance:

```
Effective Access Time = (1 - p) × memory_access_time + 
                        p × page_fault_time

Where:
p = probability of page fault (0 ≤ p ≤ 1)

Example:
Memory access = 200 ns
Page fault service time = 8 ms = 8,000,000 ns
p = 0.001 (one page fault per 1000 accesses)

EAT = 0.999 × 200 + 0.001 × 8,000,000
    = 199.8 + 8,000
    = 8,199.8 ns

For 10% performance degradation:
220 ns = 0.999 × 200 + p × 8,000,000
p = 0.0000025 = 1 / 400,000
```

## Page Replacement Algorithms

When no free frames available, must select victim page to remove.

### 1. FIFO (First-In-First-Out)

Oldest page replaced first.

```python
from collections import deque

def fifo(pages, num_frames):
    frames = deque(maxlen=num_frames)
    page_faults = 0
    
    for page in pages:
        if page not in frames:
            frames.append(page)
            page_faults += 1
    
    return page_faults
```

**Belady's Anomaly**: More frames can cause more page faults!

**Example:**
```
Reference String: 1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5

3 frames: 9 page faults
4 frames: 10 page faults (anomaly!)
```

### 2. Optimal (OPT)

Replace page not used for longest time in future.

```python
def optimal(pages, num_frames):
    frames = []
    page_faults = 0
    
    for i, page in enumerate(pages):
        if page not in frames:
            if len(frames) < num_frames:
                frames.append(page)
            else:
                # Find page used farthest in future
                farthest = -1
                victim = 0
                
                for j, frame in enumerate(frames):
                    try:
                        next_use = pages[i+1:].index(frame)
                    except ValueError:
                        # Page never used again
                        victim = j
                        break
                    
                    if next_use > farthest:
                        farthest = next_use
                        victim = j
                
                frames[victim] = page
            
            page_faults += 1
    
    return page_faults
```

**Problem**: Impossible to implement (requires future knowledge)
**Use**: Benchmark for other algorithms

### 3. Least Recently Used (LRU)

Replace page not used for longest time in past.

**Implementation Options:**

#### Counter-based:
```c
struct page {
    unsigned int frame_number;
    unsigned long counter;  // Timestamp of last use
};

// On access:
page.counter = global_counter++;

// On replacement:
// Select page with smallest counter
```

#### Stack-based:
```python
class LRU:
    def __init__(self, num_frames):
        self.frames = []
        self.capacity = num_frames
    
    def access(self, page):
        if page in self.frames:
            # Move to top (most recent)
            self.frames.remove(page)
            self.frames.append(page)
            return False  # No page fault
        else:
            if len(self.frames) >= self.capacity:
                # Remove bottom (least recent)
                self.frames.pop(0)
            self.frames.append(page)
            return True  # Page fault
```

### 4. LRU Approximation Algorithms

#### Clock (Second-Chance) Algorithm:

```python
def clock(pages, num_frames):
    frames = [None] * num_frames
    reference_bits = [0] * num_frames
    pointer = 0
    page_faults = 0
    
    for page in pages:
        # Check if page in frames
        if page in frames:
            # Set reference bit
            idx = frames.index(page)
            reference_bits[idx] = 1
        else:
            # Page fault
            while True:
                if reference_bits[pointer] == 0:
                    # Replace this page
                    frames[pointer] = page
                    reference_bits[pointer] = 1
                    pointer = (pointer + 1) % num_frames
                    break
                else:
                    # Give second chance
                    reference_bits[pointer] = 0
                    pointer = (pointer + 1) % num_frames
            
            page_faults += 1
    
    return page_faults
```

## Thrashing

**Thrashing**: Process spends more time paging than executing.

### Cause:
- Too many processes in memory
- Each process has too few frames
- Constant page faults

### Detection:
```
CPU utilization drops
Page fault rate increases dramatically
```

### Solutions:

#### 1. Working Set Model
- Working set W(t, Δ): Set of pages referenced in last Δ time units
- If total working set > available frames → thrashing

#### 2. Page Fault Frequency (PFF)
- Monitor page fault rate
- If too high: Allocate more frames
- If too low: Remove frames

### Linux Memory Management

```c
// Linux page structure
struct page {
    unsigned long flags;         // Page status flags
    atomic_t _refcount;         // Reference count
    struct address_space *mapping; // Owner
    pgoff_t index;              // Offset in file
    struct list_head lru;       // LRU list
    // ... more fields
};
```

**Buddy System**: For allocating physical memory
- Divides memory into blocks of power-of-2 sizes
- Efficient allocation and coalescing

**Slab Allocator**: For kernel objects
- Pre-allocated object caches
- Reduces allocation overhead

## Summary

Memory management is critical for system performance:
- Address binding and translation enable virtual memory
- Paging eliminates external fragmentation
- Virtual memory allows large address spaces
- Page replacement algorithms minimize page faults
- Thrashing must be avoided for good performance

### Key Takeaways:
✓ Paging provides clean memory management
✓ Multi-level page tables save space
✓ TLB critical for performance
✓ LRU is good approximation to OPT
✓ Working set model helps prevent thrashing
        '''
    }
]

with transaction.atomic():
    for lesson_data in os2_lessons_data:
        lesson, created = Lesson.objects.get_or_create(
            course=os2_course,
            title=lesson_data['title'],
            defaults={
                'content': lesson_data['content'],
                'order': lesson_data['order'],
                'difficulty': lesson_data['difficulty'],
                'estimated_time_minutes': lesson_data['estimated_time_minutes']
            }
        )
        if created:
            print(f"✅ Created lesson: {lesson.title}")
        else:
            # Update content if lesson exists
            lesson.content = lesson_data['content']
            lesson.save()
            print(f"✅ Updated lesson: {lesson.title}")
        
        # Add video resources
        if lesson_data['order'] == 1:
            Resource.objects.get_or_create(
                lesson=lesson,
                title="Operating Systems Overview (Video Tutorial)",
                defaults={
                    'kind': 'video',
                    'url': 'https://www.youtube.com/embed/26QPDBe-NB8',
                    'content': 'Comprehensive overview of operating system concepts, architecture, and components.'
                }
            )
        elif lesson_data['order'] == 2:
            Resource.objects.get_or_create(
                lesson=lesson,
                title="Process Management Explained (Video)",
                defaults={
                    'kind': 'video',
                    'url': 'https://www.youtube.com/embed/OrM7nZcxXZU',
                    'content': 'Deep dive into process scheduling algorithms, synchronization, and deadlocks.'
                }
            )
        elif lesson_data['order'] == 3:
            Resource.objects.get_or_create(
                lesson=lesson,
                title="Memory Management Tutorial (Video)",
                defaults={
                    'kind': 'video',
                    'url': 'https://www.youtube.com/embed/qdkxXygc3rE',
                    'content': 'Complete tutorial on virtual memory, paging, and page replacement algorithms.'
                }
            )

print(f"\n✅ Operating Systems 2 course populated with {len(os2_lessons_data)} lessons")

# ========== DATABASE SYSTEMS 3 ==========
print("\n📚 Creating Database Systems 3 Course...")

db3_course, created = Course.objects.get_or_create(
    title="Database Systems 3",
    defaults={
        'description': '''Advanced database systems covering query optimization, transaction management, concurrency control, and distributed databases. 
        Learn professional database design, performance tuning, and enterprise-level database management.''',
        'instructor': instructor,
        'is_published': True,
        'difficulty': 'advanced'
    }
)

if created:
    print("✅ Created Database Systems 3 course")
else:
    print("✅ Database Systems 3 course exists")

# DB3 Lessons with comprehensive content
db3_lessons_data = [
    {
        'title': 'Chapter 1: Advanced SQL and Query Optimization',
        'order': 1,
        'difficulty': 'advanced',
        'estimated_time_minutes': 100,
        'content': '''
# Advanced SQL and Query Optimization

## Introduction to Advanced SQL

SQL (Structured Query Language) is the standard language for relational database management. Advanced SQL includes complex queries, optimization techniques, and performance tuning.

## Common Table Expressions (CTEs)

CTEs provide temporary result sets that can be referenced within SELECT, INSERT, UPDATE, or DELETE statements.

### Basic CTE Syntax:

```sql
WITH cte_name AS (
    SELECT column1, column2
    FROM table
    WHERE condition
)
SELECT *
FROM cte_name;
```

### Example: Employee Hierarchy

```sql
-- Find employees and their managers
WITH EmployeeHierarchy AS (
    SELECT 
        employee_id,
        employee_name,
        manager_id,
        1 AS level
    FROM employees
    WHERE manager_id IS NULL  -- Top level
    
    UNION ALL
    
    SELECT 
        e.employee_id,
        e.employee_name,
        e.manager_id,
        eh.level + 1
    FROM employees e
    INNER JOIN EmployeeHierarchy eh 
        ON e.manager_id = eh.employee_id
)
SELECT * FROM EmployeeHierarchy
ORDER BY level, employee_name;
```

### Multiple CTEs:

```sql
WITH 
    Sales2023 AS (
        SELECT product_id, SUM(amount) as total_sales
        FROM orders
        WHERE YEAR(order_date) = 2023
        GROUP BY product_id
    ),
    TopProducts AS (
        SELECT product_id, product_name
        FROM products
        WHERE category = 'Electronics'
    )
SELECT 
    tp.product_name,
    COALESCE(s.total_sales, 0) as sales
FROM TopProducts tp
LEFT JOIN Sales2023 s ON tp.product_id = s.product_id
ORDER BY sales DESC;
```

## Recursive Queries

Recursive CTEs allow querying hierarchical or graph-like data.

### Bill of Materials Example:

```sql
WITH RECURSIVE BillOfMaterials AS (
    -- Anchor: Top-level product
    SELECT 
        product_id,
        component_id,
        quantity,
        1 AS level,
        CAST(product_id AS VARCHAR(1000)) AS path
    FROM product_components
    WHERE product_id = 'P001'
    
    UNION ALL
    
    -- Recursive: Sub-components
    SELECT 
        pc.product_id,
        pc.component_id,
        pc.quantity * bom.quantity,  -- Cumulative quantity
        bom.level + 1,
        CONCAT(bom.path, '->', pc.component_id)
    FROM product_components pc
    INNER JOIN BillOfMaterials bom 
        ON pc.product_id = bom.component_id
    WHERE bom.level < 10  -- Prevent infinite recursion
)
SELECT 
    level,
    component_id,
    quantity,
    path
FROM BillOfMaterials
ORDER BY level, component_id;
```

## Window Functions

Window functions perform calculations across rows related to the current row.

### Syntax:

```sql
function_name([arguments]) 
OVER (
    [PARTITION BY column]
    [ORDER BY column]
    [ROWS|RANGE frame_specification]
)
```

### Ranking Functions:

```sql
-- ROW_NUMBER: Unique sequential integer
SELECT 
    employee_name,
    department,
    salary,
    ROW_NUMBER() OVER (
        PARTITION BY department 
        ORDER BY salary DESC
    ) AS row_num
FROM employees;

-- RANK: Same values get same rank, gaps in sequence
SELECT 
    employee_name,
    salary,
    RANK() OVER (ORDER BY salary DESC) AS rank
FROM employees;

-- DENSE_RANK: Same values get same rank, no gaps
SELECT 
    employee_name,
    salary,
    DENSE_RANK() OVER (ORDER BY salary DESC) AS dense_rank
FROM employees;

-- NTILE: Divides rows into specified number of groups
SELECT 
    employee_name,
    salary,
    NTILE(4) OVER (ORDER BY salary DESC) AS quartile
FROM employees;
```

### Aggregate Window Functions:

```sql
-- Running total
SELECT 
    order_date,
    order_amount,
    SUM(order_amount) OVER (
        ORDER BY order_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_total
FROM orders;

-- Moving average (last 7 days)
SELECT 
    order_date,
    order_amount,
    AVG(order_amount) OVER (
        ORDER BY order_date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS moving_avg_7day
FROM daily_sales;

-- Compare with previous row
SELECT 
    order_date,
    order_amount,
    LAG(order_amount, 1) OVER (ORDER BY order_date) AS prev_amount,
    order_amount - LAG(order_amount, 1) OVER (ORDER BY order_date) AS difference
FROM orders;

-- Compare with next row
SELECT 
    order_date,
    order_amount,
    LEAD(order_amount, 1) OVER (ORDER BY order_date) AS next_amount
FROM orders;
```

## Advanced JOINs

### CROSS APPLY vs OUTER APPLY:

```sql
-- CROSS APPLY: Like INNER JOIN with table-valued function
SELECT 
    c.customer_id,
    c.customer_name,
    top_orders.order_id,
    top_orders.order_amount
FROM customers c
CROSS APPLY (
    SELECT TOP 3 order_id, order_amount
    FROM orders
    WHERE customer_id = c.customer_id
    ORDER BY order_amount DESC
) AS top_orders;

-- OUTER APPLY: Like LEFT JOIN with table-valued function
SELECT 
    c.customer_id,
    c.customer_name,
    top_orders.order_id,
    top_orders.order_amount
FROM customers c
OUTER APPLY (
    SELECT TOP 3 order_id, order_amount
    FROM orders
    WHERE customer_id = c.customer_id
    ORDER BY order_amount DESC
) AS top_orders;
```

### LATERAL JOIN (PostgreSQL):

```sql
-- Similar to CROSS APPLY
SELECT 
    c.customer_name,
    latest.order_date,
    latest.order_amount
FROM customers c,
LATERAL (
    SELECT order_date, order_amount
    FROM orders
    WHERE customer_id = c.customer_id
    ORDER BY order_date DESC
    LIMIT 1
) AS latest;
```

## Query Optimization Techniques

### 1. Use EXPLAIN/EXPLAIN ANALYZE

```sql
-- PostgreSQL
EXPLAIN ANALYZE
SELECT * 
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_date >= '2023-01-01';

-- MySQL
EXPLAIN
SELECT * 
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_date >= '2023-01-01';
```

### 2. Index Selection

**When to Create Indexes:**
- Columns used in WHERE clauses
- Columns used in JOIN conditions
- Columns used in ORDER BY
- Columns used in GROUP BY

```sql
-- Single column index
CREATE INDEX idx_order_date ON orders(order_date);

-- Composite index (order matters!)
CREATE INDEX idx_customer_date ON orders(customer_id, order_date);

-- Covering index (includes non-key columns)
CREATE INDEX idx_orders_covering 
ON orders(customer_id, order_date) 
INCLUDE (order_amount, status);

-- Partial index (PostgreSQL)
CREATE INDEX idx_active_orders 
ON orders(customer_id)
WHERE status = 'active';

-- Unique index
CREATE UNIQUE INDEX idx_email ON customers(email);
```

### 3. Query Rewriting

**Bad Query:**
```sql
-- Using OR with different columns (can't use index efficiently)
SELECT * FROM orders
WHERE customer_id = 100 OR order_date = '2023-01-01';
```

**Good Query:**
```sql
-- Use UNION to allow index usage
SELECT * FROM orders WHERE customer_id = 100
UNION
SELECT * FROM orders WHERE order_date = '2023-01-01';
```

**Bad Query:**
```sql
-- Function on indexed column prevents index usage
SELECT * FROM orders
WHERE YEAR(order_date) = 2023;
```

**Good Query:**
```sql
-- Range query allows index usage
SELECT * FROM orders
WHERE order_date >= '2023-01-01' 
  AND order_date < '2024-01-01';
```

### 4. JOIN Order Optimization

**General Rule:** Join smaller result sets first

```sql
-- Potentially slow
SELECT *
FROM large_table lt
JOIN small_table st ON lt.id = st.id
WHERE st.category = 'specific';

-- Better: Filter small table first
SELECT *
FROM small_table st
JOIN large_table lt ON st.id = lt.id
WHERE st.category = 'specific';

-- Even better: Use WITH clause
WITH filtered_small AS (
    SELECT * FROM small_table
    WHERE category = 'specific'
)
SELECT *
FROM filtered_small fs
JOIN large_table lt ON fs.id = lt.id;
```

### 5. Avoiding N+1 Query Problem

**Bad Approach:**
```sql
-- Main query
SELECT id, customer_name FROM customers;

-- Then for each customer:
SELECT order_id, order_amount 
FROM orders 
WHERE customer_id = ?;  -- Executed N times
```

**Good Approach:**
```sql
-- Single query with JOIN
SELECT 
    c.id,
    c.customer_name,
    o.order_id,
    o.order_amount
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id;

-- Or use window functions for aggregation
SELECT DISTINCT
    c.id,
    c.customer_name,
    COUNT(o.order_id) OVER (PARTITION BY c.id) as order_count,
    SUM(o.order_amount) OVER (PARTITION BY c.id) as total_amount
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id;
```

## Execution Plans

### Understanding EXPLAIN Output:

**Sequential Scan:**
- Reads entire table
- Used when no suitable index or small table
```
Seq Scan on customers  (cost=0.00..15.00 rows=1000)
```

**Index Scan:**
- Uses index to find rows
- Good for selective queries
```
Index Scan using idx_customer_id on orders  
(cost=0.42..8.44 rows=1)
```

**Index Only Scan:**
- All needed columns in index
- Doesn't access table
```
Index Only Scan using idx_covering on orders
(cost=0.42..4.44 rows=1)
```

**Nested Loop Join:**
- For each row in outer table, scan inner table
- Good for small result sets
```
Nested Loop  (cost=0.42..16.50 rows=5)
```

**Hash Join:**
- Build hash table from one relation
- Probe with other relation
- Good for large equi-joins
```
Hash Join  (cost=15.00..35.00 rows=1000)
```

**Merge Join:**
- Both inputs sorted
- Merge sorted results
- Efficient for sorted data
```
Merge Join  (cost=45.00..65.00 rows=1000)
```

### Cost Analysis:

```
cost=startup_cost..total_cost rows=estimated_rows width=average_row_width
```

- **Startup cost**: Work before first row
- **Total cost**: Work to return all rows
- **Rows**: Estimated number of rows
- **Width**: Average row size in bytes

## Statistics and Histograms

Database uses statistics to estimate costs:

```sql
-- Update statistics (PostgreSQL)
ANALYZE orders;

-- Update specific table statistics
ANALYZE customers;

-- View statistics
SELECT * FROM pg_stats WHERE tablename = 'orders';

-- MySQL
ANALYZE TABLE orders;

-- View index statistics
SHOW INDEX FROM orders;
```

## Query Hints (Use Sparingly!)

```sql
-- Force index usage (MySQL)
SELECT * FROM orders USE INDEX (idx_customer_id)
WHERE customer_id = 100;

-- Force join order (PostgreSQL)
SET join_collapse_limit = 1;
SELECT * FROM table1, table2, table3
WHERE table1.id = table2.id AND table2.id = table3.id;

-- Parallel query hint (PostgreSQL)
SET max_parallel_workers_per_gather = 4;
```

## Materialized Views

Pre-computed query results stored as tables:

```sql
-- Create materialized view
CREATE MATERIALIZED VIEW monthly_sales AS
SELECT 
    DATE_TRUNC('month', order_date) AS month,
    product_id,
    SUM(order_amount) AS total_sales,
    COUNT(*) AS order_count
FROM orders
GROUP BY DATE_TRUNC('month', order_date), product_id;

-- Create index on materialized view
CREATE INDEX idx_mv_month ON monthly_sales(month);

-- Refresh materialized view
REFRESH MATERIALIZED VIEW monthly_sales;

-- Concurrent refresh (PostgreSQL)
REFRESH MATERIALIZED VIEW CONCURRENTLY monthly_sales;
```

## Summary

Advanced SQL and query optimization are essential for database performance:
- CTEs improve query readability and maintainability
- Window functions enable complex analytical queries
- Proper indexing is crucial for performance
- Understanding execution plans helps identify bottlenecks
- Statistics must be kept up-to-date

### Key Takeaways:
✓ Use CTEs for complex queries and recursive operations
✓ Window functions enable sophisticated analytics
✓ Always check execution plans before deploying
✓ Index strategically based on query patterns
✓ Keep statistics updated for optimal query planning
        '''
    },
    {
        'title': 'Chapter 2: Transaction Management and Concurrency Control',
        'order': 2,
        'difficulty': 'advanced',
        'estimated_time_minutes': 110,
        'content': '''
# Transaction Management and Concurrency Control

## Introduction to Transactions

A **transaction** is a logical unit of work that must be completed entirely or not at all. Transactions ensure data consistency and integrity in database systems.

### ACID Properties

Every transaction must satisfy ACID properties:

#### 1. Atomicity
- **All or nothing**: Transaction either completes fully or has no effect
- If any part fails, entire transaction rolls back

**Example:**
```sql
BEGIN TRANSACTION;
    UPDATE accounts SET balance = balance - 100 WHERE account_id = 'A';
    UPDATE accounts SET balance = balance + 100 WHERE account_id = 'B';
    -- If either fails, both roll back
COMMIT;
```

#### 2. Consistency
- Transaction transforms database from one valid state to another
- Database constraints must be satisfied before and after

**Example:**
```sql
-- Constraint: balance >= 0
BEGIN TRANSACTION;
    UPDATE accounts SET balance = balance - 100 WHERE account_id = 'A';
    -- If this would make balance negative, transaction fails
COMMIT;
```

#### 3. Isolation
- Concurrent transactions do not interfere with each other
- Each transaction appears to execute in isolation

**Isolation Levels:**
- Read Uncommitted
- Read Committed
- Repeatable Read
- Serializable

#### 4. Durability
- Once committed, changes are permanent
- Survive system failures

**Implemented through:**
- Write-ahead logging (WAL)
- Database backups
- Replication

## Transaction States

```
Active → Partially Committed → Committed
   ↓
Failed → Aborted
```

### State Descriptions:

1. **Active**: Transaction is executing
2. **Partially Committed**: Final statement executed, but not yet committed
3. **Committed**: Transaction successfully completed
4. **Failed**: Normal execution cannot proceed
5. **Aborted**: Transaction rolled back, database restored to before transaction

## Concurrency Problems

Without proper concurrency control, multiple transactions can cause problems:

### 1. Lost Update Problem

Two transactions read same value and update it, second update overwrites first.

**Example:**
```
Time    T1                          T2
1       READ(X) = 100
2                                   READ(X) = 100
3       X = X - 50 = 50
4       WRITE(X) = 50
5                                   X = X - 30 = 70
6                                   WRITE(X) = 70
Result: X = 70 (T1's update lost!)
```

### 2. Dirty Read Problem

Transaction reads uncommitted data from another transaction.

**Example:**
```
Time    T1                          T2
1       READ(X) = 100
2       X = X - 50 = 50
3       WRITE(X) = 50
4                                   READ(X) = 50 (dirty read)
5       ROLLBACK
6                                   COMMIT
Result: T2 read data that never existed!
```

### 3. Unrepeatable Read Problem

Transaction reads same data twice and gets different values.

**Example:**
```
Time    T1                          T2
1       READ(X) = 100
2                                   READ(X) = 100
3                                   X = X - 50 = 50
4                                   WRITE(X) = 50
5                                   COMMIT
6       READ(X) = 50 (different!)
Result: T1 sees different value in same transaction
```

### 4. Phantom Read Problem

Transaction re-executes query and finds different number of rows.

**Example:**
```
Time    T1                                  T2
1       SELECT COUNT(*) FROM accounts      
        WHERE balance > 1000; (result: 5)
2                                           INSERT INTO accounts ...
3                                           (balance = 1500)
4                                           COMMIT
5       SELECT COUNT(*) FROM accounts      
        WHERE balance > 1000; (result: 6)
Result: T1 sees different number of rows
```

## Isolation Levels

SQL standard defines four isolation levels:

### Comparison Table:

| Level              | Dirty Read | Unrepeatable Read | Phantom Read |
|--------------------|------------|-------------------|--------------|
| Read Uncommitted   | Yes        | Yes               | Yes          |
| Read Committed     | No         | Yes               | Yes          |
| Repeatable Read    | No         | No                | Yes          |
| Serializable       | No         | No                | No           |

### Setting Isolation Level:

```sql
-- PostgreSQL
BEGIN TRANSACTION ISOLATION LEVEL READ COMMITTED;
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;

-- MySQL
SET SESSION TRANSACTION ISOLATION LEVEL REPEATABLE READ;
START TRANSACTION;

-- SQL Server
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
BEGIN TRANSACTION;
```

### Read Uncommitted

**Least strict, highest performance**

```sql
SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
BEGIN TRANSACTION;
    -- Can read uncommitted changes from other transactions
    SELECT * FROM accounts WHERE balance > 1000;
COMMIT;
```

### Read Committed (Default in most systems)

**Prevents dirty reads**

```sql
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
BEGIN TRANSACTION;
    -- Only reads committed data
    -- But may get different values on re-read
    SELECT * FROM accounts WHERE account_id = 'A';
    -- ... other operations ...
    SELECT * FROM accounts WHERE account_id = 'A'; -- Might differ
COMMIT;
```

### Repeatable Read

**Prevents dirty and unrepeatable reads**

```sql
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
BEGIN TRANSACTION;
    SELECT * FROM accounts WHERE account_id = 'A';
    -- ... other operations ...
    SELECT * FROM accounts WHERE account_id = 'A'; -- Same result
    -- But new rows might appear (phantom reads)
COMMIT;
```

### Serializable

**Strictest isolation, lowest performance**

```sql
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
BEGIN TRANSACTION;
    -- Complete isolation
    -- Transactions appear to execute serially
    SELECT * FROM accounts WHERE balance > 1000;
    -- ... operations ...
    SELECT * FROM accounts WHERE balance > 1000; -- Exactly same
COMMIT;
```

## Locking Mechanisms

Locks ensure transaction isolation by preventing concurrent access.

### Lock Types:

#### 1. Shared Lock (S-lock, Read Lock)
- Multiple transactions can hold simultaneously
- Allows reading but not writing

```sql
-- Explicit shared lock
SELECT * FROM accounts WHERE account_id = 'A' FOR SHARE;
```

#### 2. Exclusive Lock (X-lock, Write Lock)
- Only one transaction can hold
- Prevents reading and writing by others

```sql
-- Explicit exclusive lock
SELECT * FROM accounts WHERE account_id = 'A' FOR UPDATE;
```

### Lock Compatibility Matrix:

|        | S-lock | X-lock |
|--------|--------|--------|
| S-lock | Yes    | No     |
| X-lock | No     | No     |

### Lock Granularity:

- **Database Level**: Entire database locked
- **Table Level**: Entire table locked
- **Page Level**: Database page locked
- **Row Level**: Individual row locked (finest granularity)

```sql
-- Row-level lock (PostgreSQL)
BEGIN;
SELECT * FROM accounts 
WHERE account_id = 'A' 
FOR UPDATE;  -- Locks this row only

-- Table-level lock
LOCK TABLE accounts IN EXCLUSIVE MODE;
```

## Two-Phase Locking (2PL)

Protocol ensuring serializability through locking.

### Rules:

1. **Growing Phase**: Transaction acquires locks, cannot release
2. **Shrinking Phase**: Transaction releases locks, cannot acquire

### Basic 2PL:

```
Transaction T1:
1. LOCK-S(A)      -- Growing phase
2. READ(A)
3. LOCK-X(B)      -- Still growing
4. WRITE(B)
5. UNLOCK(A)      -- Shrinking phase starts
6. UNLOCK(B)      -- Still shrinking
```

### Strict 2PL:

Releases all locks only at commit/abort (most common in practice).

```
Transaction T1:
1. LOCK-S(A)
2. READ(A)
3. LOCK-X(B)
4. WRITE(B)
5. COMMIT        -- All locks released here
```

## Deadlocks

Two or more transactions waiting for each other to release locks.

### Example:

```
Time    T1                      T2
1       LOCK-X(A)
2                               LOCK-X(B)
3       Request LOCK-X(B)
        [WAITS for T2]
4                               Request LOCK-X(A)
                                [WAITS for T1]
Deadlock! Both wait forever
```

### Deadlock Handling Strategies:

#### 1. Deadlock Prevention

Ensure one of four necessary conditions cannot hold:

**Ordering Locks:**
```sql
-- All transactions must lock resources in same order
-- T1 and T2 both lock in order: A, then B
BEGIN TRANSACTION;
    LOCK(A);
    LOCK(B);
    -- ... operations ...
COMMIT;
```

**Wait-Die Scheme:**
```
If T1 wants resource locked by T2:
    If T1 older: T1 waits
    If T1 younger: T1 aborts (dies)
```

**Wound-Wait Scheme:**
```
If T1 wants resource locked by T2:
    If T1 older: T2 aborts (wounded)
    If T1 younger: T1 waits
```

#### 2. Deadlock Detection

Periodically check for cycles in wait-for graph.

```python
class DeadlockDetector:
    def __init__(self):
        self.wait_for = {}  # Transaction -> Set of transactions it waits for
    
    def add_wait(self, t1, t2):
        if t1 not in self.wait_for:
            self.wait_for[t1] = set()
        self.wait_for[t1].add(t2)
    
    def detect_cycle(self, start, current, visited, rec_stack):
        visited.add(current)
        rec_stack.add(current)
        
        if current in self.wait_for:
            for neighbor in self.wait_for[current]:
                if neighbor not in visited:
                    if self.detect_cycle(start, neighbor, visited, rec_stack):
                        return True
                elif neighbor in rec_stack:
                    return True  # Cycle detected
        
        rec_stack.remove(current)
        return False
    
    def has_deadlock(self):
        visited = set()
        for transaction in self.wait_for.keys():
            if transaction not in visited:
                if self.detect_cycle(transaction, transaction, visited, set()):
                    return True
        return False
```

**Deadlock Recovery:**
```
1. Select victim transaction (usually youngest or least work done)
2. Abort victim transaction
3. Restart victim transaction
```

## Multi-Version Concurrency Control (MVCC)

MVCC allows readers to access data without blocking writers (and vice versa).

### How MVCC Works:

1. Each write creates new version of data item
2. Each transaction sees snapshot of database at transaction start
3. Old versions maintained until no transaction needs them

### PostgreSQL MVCC Implementation:

```sql
-- Each row has hidden columns:
-- xmin: Transaction ID that created row
-- xmax: Transaction ID that deleted/updated row

CREATE TABLE accounts (
    account_id VARCHAR(10),
    balance DECIMAL(10,2),
    -- Hidden columns:
    -- xmin TRANSACTION_ID
    -- xmax TRANSACTION_ID
);
```

**Example:**

```
Initial: balance = 100 (xmin=T0, xmax=NULL)

T1 (ID=101) starts:
    Sees balance = 100

T2 (ID=102) updates balance to 150:
    Old version: balance = 100 (xmin=T0, xmax=T2)
    New version: balance = 150 (xmin=T2, xmax=NULL)

T1 still sees balance = 100 (snapshot isolation)
New transactions see balance = 150
```

### Advantages of MVCC:

- Readers don't block writers
- Writers don't block readers
- No read locks needed
- Better concurrency

### Disadvantages:

- More storage needed
- Vacuum/cleanup required
- Can have phantom reads in some isolation levels

## Optimistic Concurrency Control

Assume conflicts are rare, validate at commit time.

### Three Phases:

1. **Read Phase**: Transaction reads data, keeps local copy
2. **Validation Phase**: Check if conflicts occurred
3. **Write Phase**: If valid, make changes permanent

```python
class OptimisticTransaction:
    def __init__(self, transaction_id):
        self.id = transaction_id
        self.read_set = set()
        self.write_set = {}
        self.start_time = time.time()
    
    def read(self, item):
        value, timestamp = database.read(item)
        self.read_set.add((item, timestamp))
        return value
    
    def write(self, item, value):
        self.write_set[item] = value
    
    def validate(self):
        # Check if any item in read_set was modified
        for item, timestamp in self.read_set:
            current_timestamp = database.get_timestamp(item)
            if current_timestamp > timestamp:
                return False  # Conflict detected
        return True
    
    def commit(self):
        if self.validate():
            # Write all changes
            for item, value in self.write_set.items():
                database.write(item, value, time.time())
            return True
        else:
            # Abort and retry
            self.rollback()
            return False
```

## Recovery Techniques

### Write-Ahead Logging (WAL)

All changes logged before written to database.

**Log Record Format:**
```
<Transaction_ID, Data_Item, Old_Value, New_Value>
```

**Example:**
```
<T1, A, 100, 150>  -- T1 changed A from 100 to 150
<T1, B, 200, 180>  -- T1 changed B from 200 to 180
<T1, COMMIT>       -- T1 committed
```

### Recovery Algorithm:

```python
def recover_from_crash():
    # Scan log from beginning
    undo_list = set()
    redo_list = set()
    
    for record in log:
        if record.type == 'START':
            undo_list.add(record.transaction_id)
        elif record.type == 'COMMIT':
            undo_list.remove(record.transaction_id)
            redo_list.add(record.transaction_id)
        elif record.type == 'ABORT':
            undo_list.remove(record.transaction_id)
    
    # Redo committed transactions
    for record in log:
        if record.transaction_id in redo_list:
            database.write(record.item, record.new_value)
    
    # Undo uncommitted transactions
    for record in reversed(log):
        if record.transaction_id in undo_list:
            database.write(record.item, record.old_value)
```

### Checkpoints

Periodically save database state to reduce recovery time.

```
Timeline:
... T1 ... CHECKPOINT ... T2 ... T3 ... CRASH

Recovery:
- Start from last checkpoint
- Only need to process T2 and T3
```

## Distributed Transactions

Transactions spanning multiple databases.

### Two-Phase Commit (2PC) Protocol:

**Phase 1: Prepare Phase**
```
Coordinator → All Participants: "Prepare to commit"
Participants → Coordinator: "Ready" or "Abort"
```

**Phase 2: Commit Phase**
```
If all "Ready":
    Coordinator → All Participants: "Commit"
Else:
    Coordinator → All Participants: "Abort"
```

**Example:**
```
Coordinator (Bank A):
1. Send PREPARE to Bank B
2. Wait for READY or ABORT
3. If READY: Send COMMIT
   Else: Send ABORT

Participant (Bank B):
1. Receive PREPARE
2. Lock resources
3. Write to log
4. Send READY
5. Wait for COMMIT or ABORT
6. Execute and release locks
```

## Summary

Transaction management and concurrency control are fundamental to database reliability and performance. Understanding ACID properties, isolation levels, and locking mechanisms is essential for building robust database applications.

### Key Takeaways:
✓ ACID properties ensure transaction reliability
✓ Isolation levels balance consistency and performance
✓ Locking prevents concurrency problems
✓ Deadlocks must be detected and resolved
✓ MVCC provides better concurrency than traditional locking
✓ Recovery mechanisms ensure durability
        '''
    },
    {
        'title': 'Chapter 3: Database Design and Normalization',
        'order': 3,
        'difficulty': 'intermediate',
        'estimated_time_minutes': 90,
        'content': '''
# Database Design and Normalization

## Introduction to Database Design

Database design is the process of organizing data to minimize redundancy and dependency. Good design ensures data integrity, improves query performance, and makes maintenance easier.

### Database Design Process:

1. **Requirements Analysis**: Understand what data is needed
2. **Conceptual Design**: Create ER diagrams
3. **Logical Design**: Convert to relational schema
4. **Normalization**: Eliminate redundancy
5. **Physical Design**: Implement in DBMS

## Entity-Relationship (ER) Model

### Entities

An **entity** is an object or concept about which data is stored.

**Examples:**
- Student (entity type)
- John Smith (entity instance)
- Course
- Department

**Attributes:**
- **Simple**: Cannot be divided (e.g., student_id)
- **Composite**: Can be divided (e.g., address = street, city, zip)
- **Single-valued**: One value (e.g., birth_date)
- **Multi-valued**: Multiple values (e.g., phone_numbers)
- **Derived**: Calculated from other attributes (e.g., age from birth_date)

```
Entity: STUDENT
Attributes:
- student_id (key attribute)
- first_name
- last_name
- email
- date_of_birth
- address (composite: street, city, state, zip)
- phone_numbers (multi-valued)
- age (derived from date_of_birth)
```

### Relationships

A **relationship** is an association between entities.

**Relationship Types:**

1. **One-to-One (1:1)**
   - Each entity in A associated with at most one entity in B
   - Example: Person → Passport

2. **One-to-Many (1:N)**
   - Each entity in A associated with multiple entities in B
   - Example: Department → Employees

3. **Many-to-Many (M:N)**
   - Entities in both sets associated with multiple entities
   - Example: Students ↔ Courses

### ER Diagram Symbols:

```
Rectangle: Entity
Oval: Attribute
Diamond: Relationship
Line: Link between entities and attributes
Double line: Total participation
Double oval: Multi-valued attribute
Dashed oval: Derived attribute
Underline: Key attribute
```

### Example ER Diagram:

```
UNIVERSITY DATABASE

[STUDENT] ---- enrolls_in ---- [COURSE]
   |                              |
   |                              |
has_advisor                   has_instructor
   |                              |
   |                              |
[PROFESSOR] ---- teaches ---- [COURSE]
   |
   |
belongs_to
   |
   |
[DEPARTMENT]
```

## Relational Schema Design

### Converting ER to Relational Schema:

#### 1. Entity Sets → Relations

```
Entity: STUDENT {student_id, name, email, major}

Relation:
STUDENT(student_id, name, email, major)
Primary Key: student_id
```

#### 2. One-to-Many Relationships

```
DEPARTMENT(dept_id, dept_name)
EMPLOYEE(emp_id, name, salary, dept_id)
Foreign Key: emp_id REFERENCES DEPARTMENT(dept_id)
```

#### 3. Many-to-Many Relationships

```
STUDENT(student_id, name)
COURSE(course_id, title)
ENROLLMENT(student_id, course_id, grade, semester)
Primary Key: (student_id, course_id)
Foreign Keys: 
- student_id REFERENCES STUDENT
- course_id REFERENCES COURSE
```

## Functional Dependencies

A functional dependency X → Y means X determines Y.

**Examples:**
```
student_id → name, email, major
(student_id, course_id) → grade
ISBN → book_title, author, publisher
```

### Rules of Functional Dependencies:

#### Armstrong's Axioms:

1. **Reflexivity**: If Y ⊆ X, then X → Y
   - Example: {student_id, name} → student_id

2. **Augmentation**: If X → Y, then XZ → YZ
   - Example: If student_id → name, 
     then {student_id, email} → {name, email}

3. **Transitivity**: If X → Y and Y → Z, then X → Z
   - Example: If student_id → dept_id and dept_id → dept_name,
     then student_id → dept_name

#### Additional Rules:

4. **Union**: If X → Y and X → Z, then X → YZ
5. **Decomposition**: If X → YZ, then X → Y and X → Z

## Normalization

Normalization is the process of organizing data to reduce redundancy and improve data integrity.

### First Normal Form (1NF)

**Rule**: All attributes must be atomic (no multi-valued or composite attributes).

**Violation Example:**
```
STUDENT
| student_id | name      | phone_numbers        |
|------------|-----------|----------------------|
| S001       | John Doe  | 555-1234, 555-5678   |
```

**1NF Solution:**
```
STUDENT
| student_id | name      |
|------------|-----------|
| S001       | John Doe  |

STUDENT_PHONES
| student_id | phone_number |
|------------|--------------|
| S001       | 555-1234     |
| S001       | 555-5678     |
```

### Second Normal Form (2NF)

**Rule**: Must be in 1NF and all non-key attributes must be fully functionally dependent on the entire primary key (no partial dependencies).

**Violation Example:**
```
ENROLLMENT
| student_id | course_id | student_name | course_title | grade |
|------------|-----------|--------------|--------------|-------|
| S001       | C001      | John Doe     | Databases    | A     |

Primary Key: (student_id, course_id)
Problem: student_name depends only on student_id (partial dependency)
         course_title depends only on course_id (partial dependency)
```

**2NF Solution:**
```
STUDENT
| student_id | student_name |
|------------|--------------|
| S001       | John Doe     |

COURSE
| course_id | course_title |
|-----------|--------------|
| C001      | Databases    |

ENROLLMENT
| student_id | course_id | grade |
|------------|-----------|-------|
| S001       | C001      | A     |
```

### Third Normal Form (3NF)

**Rule**: Must be in 2NF and have no transitive dependencies (non-key attributes must not depend on other non-key attributes).

**Violation Example:**
```
EMPLOYEE
| emp_id | name      | dept_id | dept_name    | dept_location |
|--------|-----------|---------|--------------|---------------|
| E001   | John Doe  | D01     | Engineering  | Building A    |

Problem: dept_name and dept_location depend on dept_id (transitive dependency)
emp_id → dept_id → dept_name, dept_location
```

**3NF Solution:**
```
EMPLOYEE
| emp_id | name      | dept_id |
|--------|-----------|---------|
| E001   | John Doe  | D01     |

DEPARTMENT
| dept_id | dept_name    | dept_location |
|---------|--------------|---------------|
| D01     | Engineering  | Building A    |
```

### Boyce-Codd Normal Form (BCNF)

**Rule**: For every functional dependency X → Y, X must be a superkey.

**Violation Example:**
```
TEACHING_ASSIGNMENT
| course_id | instructor | room |
|-----------|------------|------|
| CS101     | Prof. A    | R101 |
| CS102     | Prof. B    | R102 |
| CS101     | Prof. A    | R101 |

Functional Dependencies:
- {course_id, instructor} → room
- instructor → room (Instructor always teaches in same room)

Problem: instructor → room violates BCNF because instructor is not a superkey
```

**BCNF Solution:**
```
INSTRUCTOR_ROOM
| instructor | room |
|------------|------|
| Prof. A    | R101 |
| Prof. B    | R102 |

TEACHING
| course_id | instructor |
|-----------|------------|
| CS101     | Prof. A    |
| CS102     | Prof. B    |
```

### Fourth Normal Form (4NF)

**Rule**: Must be in BCNF and have no multi-valued dependencies.

**Violation Example:**
```
EMPLOYEE_SKILLS_LANGUAGES
| emp_id | skill      | language |
|--------|------------|----------|
| E001   | Java       | English  |
| E001   | Java       | Spanish  |
| E001   | Python     | English  |
| E001   | Python     | Spanish  |

Problem: Skills and languages are independent multi-valued facts
```

**4NF Solution:**
```
EMPLOYEE_SKILLS
| emp_id | skill  |
|--------|--------|
| E001   | Java   |
| E001   | Python |

EMPLOYEE_LANGUAGES
| emp_id | language |
|--------|----------|
| E001   | English  |
| E001   | Spanish  |
```

## Denormalization

Sometimes, we intentionally introduce redundancy for performance.

### When to Denormalize:

1. **Read-Heavy Workload**: Reduce JOINs for faster queries
2. **Reporting**: Pre-aggregate data
3. **Historical Data**: Store snapshots

### Example:

**Normalized:**
```sql
-- Requires JOIN every time
SELECT o.order_id, c.customer_name, o.order_date, o.total
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id;
```

**Denormalized:**
```sql
-- Add customer_name to orders table
CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    customer_id INT,
    customer_name VARCHAR(100),  -- Denormalized
    order_date DATE,
    total DECIMAL(10,2)
);

-- No JOIN needed
SELECT order_id, customer_name, order_date, total
FROM orders;
```

### Handling Denormalization:

```sql
-- Use triggers to maintain consistency
CREATE TRIGGER update_customer_name
AFTER UPDATE ON customers
FOR EACH ROW
BEGIN
    UPDATE orders
    SET customer_name = NEW.customer_name
    WHERE customer_id = NEW.customer_id;
END;
```

## Indexing Strategy

Indexes speed up queries but slow down writes.

### Index Selection Guidelines:

1. **Primary Keys**: Always indexed
2. **Foreign Keys**: Index for JOIN performance
3. **WHERE Clauses**: Index frequently filtered columns
4. **ORDER BY**: Index sorted columns
5. **GROUP BY**: Index grouped columns

### Index Types:

```sql
-- B-Tree Index (default, good for range queries)
CREATE INDEX idx_salary ON employees(salary);

-- Hash Index (good for exact matches)
CREATE INDEX idx_email_hash ON users USING HASH(email);

-- Composite Index (multiple columns)
CREATE INDEX idx_name ON employees(last_name, first_name);

-- Partial Index (subset of rows)
CREATE INDEX idx_active_users ON users(email) 
WHERE active = true;

-- Covering Index (includes extra columns)
CREATE INDEX idx_employee_dept_salary 
ON employees(department_id) 
INCLUDE (salary, hire_date);
```

### Index Maintenance:

```sql
-- Rebuild index (when fragmented)
REINDEX INDEX idx_salary;

-- Analyze table (update statistics)
ANALYZE employees;

-- Monitor index usage
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,  -- Number of times index used
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan;
```

## Database Constraints

Constraints enforce data integrity.

### Types of Constraints:

```sql
CREATE TABLE employees (
    -- PRIMARY KEY: Uniquely identifies row
    emp_id INT PRIMARY KEY,
    
    -- NOT NULL: Cannot be null
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    
    -- UNIQUE: No duplicates
    email VARCHAR(100) UNIQUE,
    ssn CHAR(11) UNIQUE,
    
    -- CHECK: Custom validation
    salary DECIMAL(10,2) CHECK (salary > 0),
    age INT CHECK (age >= 18 AND age <= 65),
    
    -- DEFAULT: Default value
    hire_date DATE DEFAULT CURRENT_DATE,
    status VARCHAR(20) DEFAULT 'active',
    
    -- FOREIGN KEY: References another table
    dept_id INT,
    FOREIGN KEY (dept_id) REFERENCES departments(dept_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    
    -- Composite constraints
    CONSTRAINT valid_dates CHECK (hire_date <= CURRENT_DATE)
);

-- Add constraint later
ALTER TABLE employees
ADD CONSTRAINT chk_positive_salary CHECK (salary > 0);

-- Drop constraint
ALTER TABLE employees
DROP CONSTRAINT chk_positive_salary;
```

### Referential Integrity Actions:

```sql
-- ON DELETE options:
-- CASCADE: Delete child rows when parent deleted
-- SET NULL: Set foreign key to NULL
-- SET DEFAULT: Set foreign key to default value
-- RESTRICT: Prevent deletion if child rows exist
-- NO ACTION: Similar to RESTRICT

CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    customer_id INT,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        ON DELETE CASCADE  -- Delete orders when customer deleted
);
```

## Summary

Database design and normalization are fundamental to creating efficient, maintainable databases. Understanding normal forms helps eliminate redundancy, while strategic denormalization and indexing improve performance.

### Key Takeaways:
✓ ER modeling helps visualize database structure
✓ Normalization eliminates redundancy and anomalies
✓ BCNF is usually the target normal form
✓ Denormalization can improve read performance
✓ Proper indexing is crucial for query performance
✓ Constraints enforce data integrity
        '''
    }
]

with transaction.atomic():
    for lesson_data in db3_lessons_data:
        lesson, created = Lesson.objects.get_or_create(
            course=db3_course,
            title=lesson_data['title'],
            defaults={
                'content': lesson_data['content'],
                'order': lesson_data['order'],
                'difficulty': lesson_data['difficulty'],
                'estimated_time_minutes': lesson_data['estimated_time_minutes']
            }
        )
        if created:
            print(f"✅ Created lesson: {lesson.title}")
        else:
            lesson.content = lesson_data['content']
            lesson.save()
            print(f"✅ Updated lesson: {lesson.title}")
        
        # Add video resources
        if lesson_data['order'] == 1:
            Resource.objects.get_or_create(
                lesson=lesson,
                title="SQL Query Optimization Tutorial (Video)",
                defaults={
                    'kind': 'video',
                    'url': 'https://www.youtube.com/embed/BHwzDmr6d7s',
                    'content': 'Complete guide to SQL query optimization techniques and best practices.'
                }
            )
        elif lesson_data['order'] == 2:
            Resource.objects.get_or_create(
                lesson=lesson,
                title="Database Transactions and ACID (Video)",
                defaults={
                    'kind': 'video',
                    'url': 'https://www.youtube.com/embed/pomxJOFVcQs',
                    'content': 'In-depth explanation of database transactions, ACID properties, and concurrency control.'
                }
            )
        elif lesson_data['order'] == 3:
            Resource.objects.get_or_create(
                lesson=lesson,
                title="Database Normalization Explained (Video)",
                defaults={
                    'kind': 'video',
                    'url': 'https://www.youtube.com/embed/GFQaEYEc8_8',
                    'content': 'Step-by-step guide to database normalization from 1NF to BCNF.'
                }
            )

print(f"\n✅ Database Systems 3 course populated with {len(db3_lessons_data)} lessons")

print("\n" + "="*60)
print("🎉 Content Population Complete!")
print("="*60)
print(f"\n📊 Summary:")
print(f"  • Created/Updated 2 courses")
print(f"  • Created/Updated {len(os2_lessons_data) + len(db3_lessons_data)} comprehensive lessons")
print(f"  • Added {len(os2_lessons_data) + len(db3_lessons_data)} video resources")
print(f"\n✅ Students can now study directly from the website!")
print(f"✅ All lessons have comprehensive notes and video tutorials!")
print(f"\n📚 Visit your website to see the content!")
