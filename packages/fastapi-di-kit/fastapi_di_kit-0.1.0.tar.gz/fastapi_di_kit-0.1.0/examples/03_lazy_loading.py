"""
Lazy Loading Example

This example demonstrates how to use Lazy[T] to defer expensive
dependency initialization until actually needed.

Benefits:
- Faster startup time
- Only load what you use
- Break circular dependencies
"""

import time
from fastapi_di_kit import service, Lazy, get_container


@service()
class HeavyAnalyticsEngine:
    """
    Simulates a heavy service that's expensive to initialize.
    Examples: ML models, large datasets, external connections
    """
    
    def __init__(self):
        print("⏳ Initializing HeavyAnalyticsEngine...")
        time.sleep(1)  # Simulate expensive initialization
        print("✓ HeavyAnalyticsEngine ready!")
        self.model_loaded = True
    
    def analyze(self, data: str) -> str:
        return f"Analysis result for: {data}"


@service()
class QuickReportGenerator:
    """
    Service that sometimes needs analytics, sometimes doesn't.
    Using Lazy loading to avoid initializing analytics unless needed.
    """
    
    def __init__(self, analytics: Lazy[HeavyAnalyticsEngine]):
        print("✓ QuickReportGenerator initialized (no analytics loaded yet)")
        self._analytics = analytics
        self.report_count = 0
    
    def generate_simple_report(self) -> str:
        """Generate a simple report without analytics."""
        self.report_count += 1
        return f"Simple Report #{self.report_count}"
    
    def generate_detailed_report(self, data: str) -> str:
        """Generate detailed report - NOW we need analytics."""
        print("📊 Detailed report requested, loading analytics...")
        
        # Analytics engine is only initialized when we call this
        analytics = self._analytics()  # or self._analytics.value
        
        result = analytics.analyze(data)
        return f"Detailed Report: {result}"


@service()
class RegularReportGenerator:
    """
    Same service WITHOUT lazy loading - for comparison.
    Analytics is initialized immediately, even if never used.
    """
    
    def __init__(self, analytics: HeavyAnalyticsEngine):
        print("✓ RegularReportGenerator initialized (analytics loaded)")
        self.analytics = analytics
        self.report_count = 0
    
    def generate_simple_report(self) -> str:
        """Generate a simple report without analytics."""
        self.report_count += 1
        return f"Simple Report #{self.report_count}"


def demo_lazy_loading():
    """Demonstrate the performance benefit of lazy loading."""
    print("=" * 60)
    print("Lazy Loading Demo - fastapi-di-kit")
    print("=" * 60)
    print()
    
    container = get_container()
    
    print("Scenario 1: WITH lazy loading")
    print("-" * 60)
    start = time.time()
    
    # Create lazy factory manually for demonstration
    from fastapi_di_kit import Lazy
    
    def create_report_gen_lazy():
        lazy_analytics = Lazy(lambda: container.resolve(HeavyAnalyticsEngine))
        return QuickReportGenerator(lazy_analytics)
    
    container.register(QuickReportGenerator, factory=create_report_gen_lazy)
    
    quick_gen = container.resolve(QuickReportGenerator)
    init_time = time.time() - start
    
    print(f"⚡ Initialization time: {init_time:.2f}s (fast!)")
    print()
    
    # Use it without analytics
    print("Generating simple reports (no analytics needed):")
    for i in range(3):
        report = quick_gen.generate_simple_report()
        print(f"  • {report}")
    
    print()
    print("Now generating detailed report (analytics needed):")
    detailed = quick_gen.generate_detailed_report("sales data")
    print(f"  • {detailed}")
    
    print()
    print("=" * 60)
    print()
    
    # Reset for comparison
    container = get_container()
    container.register(HeavyAnalyticsEngine)
    
    print("Scenario 2: WITHOUT lazy loading")
    print("-" * 60)
    start = time.time()
    
    container.register(RegularReportGenerator)
    regular_gen = container.resolve(RegularReportGenerator)
    init_time = time.time() - start
    
    print(f"🐌 Initialization time: {init_time:.2f}s (slow!)")
    print()
    
    print("Generating simple reports:")
    for i in range(3):
        report = regular_gen.generate_simple_report()
        print(f"  • {report}")
    
    print()
    print("=" * 60)
    print()
    print("Key Takeaway:")
    print("  Lazy loading defers expensive initialization until needed,")
    print("  improving startup performance and reducing resource usage.")
    print("=" * 60)
    print()


def demo_lazy_caching():
    """Demonstrate that Lazy caches the instance."""
    print("=" * 60)
    print("Lazy Caching Demo")
    print("=" * 60)
    print()
    
    container = get_container()
    container.register(HeavyAnalyticsEngine, lifecycle=Lifecycle.TRANSIENT)
    
    from fastapi_di_kit import Lazy
    
    lazy = Lazy(lambda: container.resolve(HeavyAnalyticsEngine))
    
    print("Creating lazy wrapper (no initialization yet)...")
    print()
    
    print("First access:")
    instance1 = lazy()
    print()
    
    print("Second access (should use cached instance):")
    instance2 = lazy()
    print()
    
    print(f"Same instance? {instance1 is instance2}")
    print("(Even though lifecycle is TRANSIENT, Lazy caches it)")
    print()


if __name__ == "__main__":
    demo_lazy_loading()
    print("\n\n")
    demo_lazy_caching()
