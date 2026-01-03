from setuptools import setup, find_packages

setup(
    name="prometheus-edqt",
    version="1.0.0",
    author="Prometheus Open Science Foundation",
    author_email="contact@prometheus-science.org",
    description="Riemannian Manifold Optimization & Telemetric Integrity for AI Tensors",
    long_description="A standard implementation of Information Geometry constraints for Deep Learning, ensuring Flat Minima convergence and preventing Topological Collapse via Telemetric Synchronization.",
    long_description_content_type="text/markdown",
    url="https://github.com/Prometheus-Lab-Core/prometheus-edqt",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Mathematics", 
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires='>=3.9',
    install_requires=[
        "numpy>=1.21.0",      
        "scipy>=1.7.0",       
        "requests>=2.26.0",   
        "cryptography>=3.4.0" 
    ],
    keywords="ai machine-learning manifold-optimization information-geometry edqt-standard",
)
