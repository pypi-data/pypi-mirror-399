def check_cuda():
    try:
        import torch
        cuda_available = torch.cuda.is_available()

        result = {
            "cuda_available": cuda_available
        }

        if cuda_available:
            device = torch.device("cuda")
            import time

            x = torch.randn((8000, 8000), device=device)
            start = time.time()
            y = x @ x
            torch.cuda.synchronize()
            end = time.time()

            result["gpu_name"] = torch.cuda.get_device_name(0)
            result["benchmark_time_sec"] = round(end - start, 4)

        return result

    except Exception as e:
        return {"cuda_available": False, "error": str(e)}
