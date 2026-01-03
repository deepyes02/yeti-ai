"""
Performance profiling script to identify bottlenecks in the agent response time.
"""
import asyncio
import time
from app.call_the_model import stream_model_output_new

async def test_simple_query():
    """Test a simple query and measure time for each phase."""
    prompt = "Hello, how are you?"
    
    print("=" * 60)
    print("Testing performance with simple query: 'Hello, how are you?'")
    print("=" * 60)
    
    start_total = time.time()
    
    # Track first chunk time (TTFB - Time To First Byte)
    first_chunk = None
    chunk_count = 0
    
    async for chunk in stream_model_output_new(prompt, thread_id=999):
        if first_chunk is None:
            first_chunk = time.time()
            ttfb = first_chunk - start_total
            print(f"\n⏱️  Time to first chunk: {ttfb:.2f}s")
            print(f"📦 First chunk: {chunk}\n")
        
        chunk_count += 1
        if chunk.get("type") == "chunk":
            print(chunk["data"], end="", flush=True)
    
    end_total = time.time()
    total_time = end_total - start_total
    
    print(f"\n\n{'=' * 60}")
    print(f"✅ Total time: {total_time:.2f}s")
    print(f"📊 Total chunks: {chunk_count}")
    print(f"⚡ Time to first chunk: {ttfb:.2f}s ({(ttfb/total_time)*100:.1f}% of total)")
    print(f"{'=' * 60}\n")

if __name__ == "__main__":
    asyncio.run(test_simple_query())
