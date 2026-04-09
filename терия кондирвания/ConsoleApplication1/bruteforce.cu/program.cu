#include <stdio.h>
#include <stdint.h>

#define PASSWORD_LENGTH 8
#define CHARSET "abcdefghijklmnopqrstuvwxyz0123456789"

__device__ const char d_charset[] = CHARSET;

__device__ int found = 0;
__device__ char result[PASSWORD_LENGTH + 1];

__device__ void indexToPassword(uint64_t index, char* guess, int base)
{
    for (int i = PASSWORD_LENGTH - 1; i >= 0; i--)
    {
        guess[i] = d_charset[index % base];
        index /= base;
    }
}

__global__ void bruteForceKernel(uint64_t total, const char* target, int base)
{
    uint64_t idx = blockIdx.x * blockDim.x + threadIdx.x;
    uint64_t stride = blockDim.x * gridDim.x;

    char guess[PASSWORD_LENGTH];

    for (uint64_t i = idx; i < total; i += stride)
    {
        if (found) return;

        indexToPassword(i, guess, base);

        bool match = true;
        for (int j = 0; j < PASSWORD_LENGTH; j++)
        {
            if (guess[j] != target[j])
            {
                match = false;
                break;
            }
        }

        if (match)
        {
            found = 1;
            for (int k = 0; k < PASSWORD_LENGTH; k++)
                result[k] = guess[k];
            result[PASSWORD_LENGTH] = '\0';
        }
    }
}

int main()
{
    const char target[PASSWORD_LENGTH] = "t7gyh8uj";
    const int base = 36;

    uint64_t total = 1;
    for (int i = 0; i < PASSWORD_LENGTH; i++)
        total *= base;

    char* d_target;
    cudaMalloc(&d_target, PASSWORD_LENGTH);
    cudaMemcpy(d_target, target, PASSWORD_LENGTH, cudaMemcpyHostToDevice);

    int threads = 256;
    int blocks = 1024;

    bruteForceKernel << <blocks, threads >> > (total, d_target, base);
    cudaDeviceSynchronize();

    int h_found;
    char h_result[PASSWORD_LENGTH + 1];

    cudaMemcpyFromSymbol(&h_found, found, sizeof(int));
    cudaMemcpyFromSymbol(h_result, result, PASSWORD_LENGTH + 1);

    if (h_found)
        printf("Password found: %s\n", h_result);
    else
        printf("Password not found\n");

    cudaFree(d_target);
    return 0;
}