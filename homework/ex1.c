#include <stdio.h>
#include <string.h>   /* For strlen    */
#include <mpi.h>      /* For MPI functions, etc */

const int MAX_STRING = 100;

/*
    Task:
    Write a program that takes data from process zero and sends it to all of
    the other processes by sending it in a ring. That is, process i should
    receive the data and send it to process i+1, until the last process is
    reached. Then define the PBS script and command to submit your job
*/

int main(void) {
    int comm_sz;   /* Number of processes */
    int my_rank;   /* My process rank     */

    MPI_Init(NULL, NULL);
    MPI_Comm_size(MPI_COMM_WORLD, &comm_sz);
    MPI_Comm_rank(MPI_COMM_WORLD, &my_rank);

    if (my_rank == 0) {
        // Process 0 intiating the secret message
        char* msg = "Secret message";
        printf("Im process %d and im sending a message to process %d!\n",  my_rank, my_rank+1);
        MPI_Send(msg, strlen(msg)+1, MPI_CHAR, my_rank+1, 0, MPI_COMM_WORLD);
    } else if(my_rank == comm_sz-1){
        // The last process needs to stop and tell us the secret
        char msg[MAX_STRING];
        MPI_Recv(msg, MAX_STRING, MPI_CHAR, my_rank-1, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
        printf("Im process %d and the secret message is %s\n",  my_rank, msg);
    } else {
        // Taking the message from the previous process and then sending it to the next one
        char msg[MAX_STRING];
        MPI_Recv(msg, MAX_STRING, MPI_CHAR, my_rank-1, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
        printf("Im process %d and im whispering to process %d\n",  my_rank, my_rank+1);
        MPI_Send(msg, strlen(msg)+1, MPI_CHAR, my_rank+1, 0, MPI_COMM_WORLD);
    }

    MPI_Finalize();
    return 0;
} /* main */
