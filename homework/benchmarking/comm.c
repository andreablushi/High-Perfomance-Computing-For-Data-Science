#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <mpi.h>

#define MAX_SIZE (1 << 20) // 1 MiB

/*
 Simple send-receive benchmark to measure time and bandwidth
 for message sizes doubling each iteration up to 1 MB.
*/
int main(int argc, char** argv) {
    int my_rank, comm_size;
    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &my_rank);
    MPI_Comm_size(MPI_COMM_WORLD, &comm_size);

    // Allow only 2 processes (ping-pong)
    if (comm_size > 2) {
        if (my_rank == 0)
            printf("Too many processes (use 2 max)\n");
        MPI_Finalize();
        return 0;
    }

    // Header for CSV output
    if (my_rank == 0) {
        printf("# n, time(sec), RATE(MB/SEC)\n");
        fflush(stdout);
    }

    // Allocate a single buffer for all message sizes
    char *buf = (char*) malloc(MAX_SIZE);
    if (!buf) {
        fprintf(stderr, "Rank %d: malloc failed for size %d\n", my_rank, MAX_SIZE);
        MPI_Abort(MPI_COMM_WORLD, 1);
    }

    size_t size;
    for (size = 1; size <= MAX_SIZE; size <<= 1) {
        int tag = 100 + (int)size; // unique tag per message size

        // Warm-up phase (not measured)
        if (my_rank == 0) {
            MPI_Send(buf, (int)size, MPI_BYTE, 1, tag, MPI_COMM_WORLD);
            MPI_Recv(buf, (int)size, MPI_BYTE, 1, tag, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
        } else {
            MPI_Recv(buf, (int)size, MPI_BYTE, 0, tag, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
            MPI_Send(buf, (int)size, MPI_BYTE, 0, tag, MPI_COMM_WORLD);
        }

        // Synchronize before timing
        MPI_Barrier(MPI_COMM_WORLD);

        // Timed communication
        double t_start = MPI_Wtime();
        if (my_rank == 0) {
            MPI_Send(buf, (int)size, MPI_BYTE, 1, tag, MPI_COMM_WORLD);
            MPI_Recv(buf, (int)size, MPI_BYTE, 1, tag, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
        } else {
            MPI_Recv(buf, (int)size, MPI_BYTE, 0, tag, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
            MPI_Send(buf, (int)size, MPI_BYTE, 0, tag, MPI_COMM_WORLD);
        }
        double t_end = MPI_Wtime();

        // Only rank 0 prints the result
        if (my_rank == 0) {
            double time = t_end - t_start; // Total round-trip time
            double one_way = time / 2.0;   // One direction
            double size_MB = ((double)size) / (1024.0 * 1024.0);
            double rate = (one_way > 0.0) ? (size_MB / one_way) : 0.0;
            printf("%zu, %.9f, %.6f\n", size, time, rate);
            fflush(stdout);
        }
    }

    free(buf);
    MPI_Finalize();
    return 0;
}
