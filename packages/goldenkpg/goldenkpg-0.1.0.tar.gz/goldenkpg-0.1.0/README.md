# goldenkpg 🌟

**goldenkpg** ("Golden Key Package Generator") is a fully scalable Python CLI tool that generates READY-MADE Python program templates for Operating System algorithms.

Designed for students and developers who need instant access to standard OS algorithms for **CPU scheduling (Brain)**, **Disk scheduling (Heart)**, and **Paging (Liver)**.

---

## 🛠 Installation

You can install the package locally:

```bash
git clone <repository-url>
cd goldenkpg
pip install .
```

Or run directly if configured.

---

## 🚀 Usage

The CLI uses **human-body metaphors** as keywords:

- **brain**  → CPU Scheduling Algorithms
- **heart**  → Disk Scheduling Algorithms
- **liver**  → Paging / Memory Management Algorithms

### 1️⃣ Generate a Template

Run the command with a keyword:

```bash
goldenkpg brain
```

**What happens:**
1.  Lists available templates (e.g., FCFS, SJF, Round Robin).
2.  Asks you to choose one.
3.  Generates a clean, runnable Python file (e.g., `fcfs.py`) in your current directory.

### 2️⃣ Other Commands

```bash
goldenkpg heart   # For disk scheduling
goldenkpg liver   # For paging algorithms
goldenkpg help    # Show all available commands and descriptions
```

---

## 📂 Available Algorithms

### 🧠 Brain (CPU Scheduling)
- **FCFS** (First-Come, First-Served)
- **SJF** (Shortest Job First)
- **Priority** Scheduling
- **Round Robin**

### ❤️ Heart (Disk Scheduling)
- **FCFS** (First-Come, First-Served)
- **SSTF** (Shortest Seek Time First)
- **SCAN** (Elevator Algorithm)
- **C-SCAN** (Circular SCAN)

### 🧪 Liver (Paging Algorithms)
- **FIFO** (First-In, First-Out)
- **LRU** (Least Recently Used)
- **Optimal** Page Replacement
- **Clock** Algorithm

---

## 🏗 Contributing

Adding new templates is easy!

1.  Create a new folder in `goldenkpg/templates/` (e.g., `lungs` for Threading).
2.  Add your Python implementation files there.
3.  The CLI automatically detects the new category and files!

---

License: MIT
