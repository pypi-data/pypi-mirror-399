# miu-code Project Roadmap

**Current Version:** 0.2.0
**Roadmap Updated:** 2025-12-31
**Long-term Vision:** Full-featured AI coding assistant with ecosystem support

## Vision Statement

miu-code aims to become the most accessible and powerful AI-assisted coding tool for developers. By combining intelligent reasoning, intuitive interfaces, and deep editor integration, we enable developers to work faster and more confidently across any codebase.

## Release Timeline

### Phase 0: Foundation (Completed)
**Status:** ✅ COMPLETE (v0.1.0)

- Basic CLI interface
- Core tool set (read, write, edit, bash)
- Single model support (Claude)

### Phase 1: Enhancement (Completed)
**Status:** ✅ COMPLETE (v0.2.0)

**Key Features:**
- ✅ TUI interface with Textual framework
- ✅ Multi-model provider support (Anthropic, OpenAI, Google)
- ✅ Session persistence with JSONLines format
- ✅ Advanced tools (glob, grep, edit)
- ✅ ACP server scaffolding
- ✅ Command system (/cook, /commit, /plan)
- ✅ 100% mypy type safety
- ✅ 80%+ test coverage

**Deliverables:**
- CLI with one-shot and REPL modes
- TUI with streaming and spinners
- 6 fully functional tools
- Session management
- Comprehensive documentation

### Phase 2: Intelligence (Q1-Q2 2025)
**Status:** 🔄 IN PROGRESS

**Target:** v0.3.0

**Features:**
- [ ] Advanced safety modes (ASK, NORMAL, PLAN)
  - ASK: Approve all tool executions
  - NORMAL: Auto-approve safe operations
  - PLAN: Planning-only mode with warnings
- [ ] Tool approval system in TUI
  - Visual preview of tool actions
  - Confirmation dialogs
  - Tool parameter review
- [ ] Enhanced input system
  - Multi-line input with wrapping
  - Code block syntax highlighting
  - Completion suggestions
- [ ] Message types
  - Thinking/reasoning messages
  - Code blocks with syntax highlighting
  - Tool execution traces
- [ ] Session management UI
  - View session history
  - Search sessions
  - Resume from checkpoint

**Implementation Focus:**
1. Tool approval dialogs
2. Mode system (ASK/NORMAL/PLAN)
3. Enhanced message rendering
4. Session UI improvements

**Testing:**
- Unit tests for modes
- Integration tests for approvals
- Widget tests for TUI additions

**Documentation:**
- Safety modes guide
- Tool approval process
- Session management guide

### Phase 3: Integration (Q2-Q3 2025)
**Status:** 📋 PLANNED

**Target:** v0.4.0

**Features:**
- [ ] Editor integrations
  - VS Code extension
  - JetBrains plugin via ACP
  - Vim/Neovim integration
- [ ] MCP (Model Context Protocol) support
  - Standard MCP integration
  - Custom MCP servers
  - Tool discovery from MCP
- [ ] Custom command framework
  - Build custom /commands easily
  - Share command templates
  - Version management
- [ ] Workflow automation
  - Bash script integration
  - GitHub Actions compatible
  - CI/CD hooks

**Implementation Focus:**
1. MCP server implementation
2. Editor plugin scaffolds
3. Custom command builder
4. CI/CD integration guide

**Testing:**
- MCP protocol tests
- Editor extension tests
- End-to-end workflows

**Documentation:**
- MCP integration guide
- VS Code extension tutorial
- Custom command guide
- CI/CD examples

### Phase 4: Optimization (Q3-Q4 2025)
**Status:** 📋 PLANNED

**Target:** v0.5.0

**Features:**
- [ ] Performance optimizations
  - Caching for repeated queries
  - Parallel tool execution
  - Memory optimization
  - Streaming improvements
- [ ] Large codebase support
  - Index-based search
  - Chunked processing
  - Lazy loading
- [ ] Advanced memory
  - Conversation summarization
  - Vector embeddings
  - Semantic search
- [ ] Observability
  - Metrics collection
  - Performance profiling
  - Query logging

**Implementation Focus:**
1. Response caching
2. Vector search integration
3. Performance profiling
4. Telemetry system

**Testing:**
- Performance benchmarks
- Load testing
- Large codebase tests

**Documentation:**
- Performance tuning guide
- Large codebase best practices
- Observability setup

### Phase 5: Stability (Q4 2025 - Q1 2026)
**Status:** 📋 PLANNED

**Target:** v1.0.0 - Production Ready

**Focus:**
- Bug fixes from beta testing
- Documentation completeness
- Security audit
- Performance tuning
- Stability validation

**Deliverables:**
- Stable API
- Production deployment guide
- Security documentation
- Performance benchmarks
- Full migration guide from v0.x

**Quality Gates:**
- 95%+ test coverage
- Zero critical security issues
- <100ms latency (p95)
- Zero crashes in production testing

### Phase 6: Ecosystem (2026+)
**Status:** 📋 VISION

**Target:** v2.0.0+

**Features:**
- [ ] Plugin system
  - Community tools
  - Custom providers
  - Workflow plugins
- [ ] Collaborative features
  - Shared sessions
  - Real-time collaboration
  - Team workspace
- [ ] Enterprise features
  - SSO integration
  - Audit logging
  - Rate limiting
  - On-premises deployment
- [ ] Platform support
  - Web interface
  - Mobile app (API)
  - Desktop app
  - VS Code integrated terminal

## Feature Priority Matrix

### High Priority (Next 6 months)
| Feature | Release | Effort | Impact |
|---------|---------|--------|--------|
| Safety modes (ASK/NORMAL/PLAN) | v0.3 | Medium | High |
| Tool approval system | v0.3 | Medium | High |
| VS Code integration | v0.4 | High | High |
| MCP support | v0.4 | High | High |
| Session management UI | v0.3 | Medium | Medium |
| Enhanced error messages | v0.3 | Low | High |

### Medium Priority (6-12 months)
| Feature | Release | Effort | Impact |
|---------|---------|--------|--------|
| Response caching | v0.5 | Medium | Medium |
| Vector embeddings | v0.5 | High | Medium |
| JetBrains plugin | v0.4 | High | Medium |
| Custom command builder | v0.4 | Medium | Medium |
| Performance profiling | v0.5 | Low | Medium |
| Advanced memory | v0.5 | High | Low |

### Low Priority (12+ months)
| Feature | Release | Effort | Impact |
|---------|---------|--------|--------|
| Vim/Neovim integration | v1.1 | Medium | Low |
| Collaborative sessions | v2.0 | High | Medium |
| Enterprise features | v2.0 | High | Low |
| Mobile app | v2.0 | Very High | Low |
| Web interface | v2.0 | High | Low |

## Dependency Evolution

### v0.2 Dependencies (Current)
```toml
textual = ">=1.0.0"      # TUI framework
asyncclick = ">=8.1"     # CLI
rich = ">=13.0"          # Formatting
prompt-toolkit = ">=3.0" # Input
miu-core = "[anthropic]" # Agent framework
```

### v0.3 Dependencies (Planned)
```toml
# Add for enhanced features
pydantic = ">=2.0"       # Data validation
msgspec = ">=0.18"       # Fast serialization
pyzmq = ">=25.0"         # MCP messaging (optional)
```

### v0.4+ Dependencies (Future)
```toml
# Optional: Editor integrations
lsp-types = "*"          # Language Server Protocol
watchdog = ">=3.0"       # File watching
jinja2 = ">=3.0"         # Template rendering
```

## Success Metrics

### User Adoption
- GitHub stars: 1K+ (by v1.0)
- PyPI downloads: 10K+/month (by v1.0)
- Community contributions: 20+ (by v1.0)
- Plugin count: 10+ (by v2.0)

### Product Quality
- Bug resolution time: <24 hours (critical)
- Test coverage: >95% (by v1.0)
- Security issues: 0 (by v1.0)
- Performance: <100ms p95 latency (by v0.5)

### Developer Experience
- Time to first query: <5 minutes
- Documentation completeness: 100%
- API stability: Semantic versioning
- Breaking changes: None without major version

### Community Health
- Issue response time: <48 hours
- Monthly PRs: 10+ (by v1.0)
- Active contributors: 15+ (by v1.0)
- Community tools: 10+ (by v2.0)

## Known Limitations & Future Work

### Current Limitations (v0.2)
1. **Single working directory** - Can't work across projects simultaneously
2. **No file indexing** - Grep scans all files
3. **No caching** - Repeated queries execute from scratch
4. **Limited memory** - No summarization of old messages
5. **Basic error messages** - Need improvement for common issues

### Planned Solutions (v0.3+)

| Limitation | Solution | Target Version |
|-----------|----------|-----------------|
| Single working directory | Workspace support | v1.0 |
| No file indexing | Index-based search | v0.5 |
| No caching | Query caching | v0.5 |
| Limited memory | Message summarization | v0.5 |
| Basic errors | AI error explanations | v0.4 |
| No offline | Offline mode with cache | v1.1 |
| Limited customization | Plugin system | v2.0 |

## Breaking Changes & Migration Path

### v0.2 → v0.3
- **No breaking changes** to public APIs
- New optional parameters for safety modes
- Migration guide provided for recommended updates

### v0.3 → v1.0
- Session format may change (auto-migration provided)
- Config file format standardized
- Deprecation warnings in v0.9

### v1.0 → v2.0 (Future)
- Plugin API stabilization
- Provider API enhancement
- Documented migration path

## Community & Contributing

### How to Get Involved

**Current Needs:**
- Bug reports and testing
- Documentation improvements
- Example workflows
- Tool suggestions

**Future Opportunities:**
- Custom tool development (v0.4)
- Editor plugin creation (v0.4)
- MCP server implementation (v0.4)
- Command template sharing

### Contribution Guidelines
- See [`CONTRIBUTING.md`](../CONTRIBUTING.md)
- Follow [Code Standards](./code-standards.md)
- Join discussions for feature requests
- Monthly community calls

## Budget & Resources

### Development
- Primary maintainer: Full-time
- Core contributors: Part-time
- Community: Volunteers

### Infrastructure
- GitHub Actions: CI/CD
- PyPI: Package hosting
- Documentation: GitHub Pages

### Support
- GitHub Issues: Community support
- Discussions: Feature requests
- Email: Critical issues

## Related Projects

### Dependencies
- [miu-core](https://github.com/vanducng/miumono) - Agent framework
- [Textual](https://github.com/Textualize/textual) - TUI framework
- [asyncclick](https://github.com/python-trio/asyncclick) - Async CLI
- [Rich](https://github.com/Textualize/rich) - Formatting

### Inspirations
- [mistral-vibe](https://github.com/mistralai/mistral-vibe) - TUI design
- [Cursor](https://cursor.sh) - AI-assisted editor
- [GitHub Copilot](https://github.com/features/copilot) - AI coding
- [LLaMA Index](https://www.llamaindex.ai) - Memory & context

### Ecosystem
- VS Code extension (planned)
- JetBrains plugin (planned)
- Vim plugin (planned)
- Language servers (planned)

## Questions & Feedback

**How to provide feedback:**
1. GitHub Discussions for feature requests
2. GitHub Issues for bugs
3. GitHub Discussions for general feedback
4. Email for sensitive security issues

**FAQs:**
- **Q: Why not merge with miu-core?**
  A: Separation allows independent evolution. miu-code is a consumer of miu-core.

- **Q: Will there be a Web interface?**
  A: Planned for v2.0+, as optional. CLI/TUI remain primary.

- **Q: Can I use miu-code offline?**
  A: Requires API keys for LLMs. Local LLM support planned for v1.1.

- **Q: How do I contribute?**
  A: See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

## Final Notes

This roadmap is a living document. Priorities may shift based on:
- Community feedback
- Technology changes
- Resource availability
- Market needs

Check back regularly for updates!

**Last updated:** 2025-12-31
**Next review:** 2026-03-31
