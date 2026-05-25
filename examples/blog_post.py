"""
Example: Generate a blog post on any topic.
Run: python examples/blog_post.py
"""
from nexus import Orchestrator

orchestrator = Orchestrator(output_format="blog")
result = orchestrator.run("Why are AI agents the future of software development?")

with open("blog_post.md", "w") as f:
    f.write(result)

print("\nBlog post saved to blog_post.md")
