"""Tests for GraphDocument and graph rendering."""

import pytest

from llb_doc import NodeNotFoundError, create_graph
from llb_doc.core import Ctx, Edge, Node


class TestGraphDocumentBasic:
    """Test basic GraphDocument functionality."""

    def test_create_graph(self):
        g = create_graph("test-graph")
        assert g.graph_id == "test-graph"
        assert len(g.nodes) == 0
        assert len(g.edges) == 0

    def test_add_node(self):
        g = create_graph()
        node = g.add_node("person", "Alice content", name="Alice")
        assert node.id == "N1"
        assert node.type == "person"
        assert node.content == "Alice content"
        assert node.meta["name"] == "Alice"
        assert len(g.nodes) == 1

    def test_add_node_with_custom_id(self):
        g = create_graph()
        node = g.add_node("person", id_="custom-node")
        assert node.id == "custom-node"

    def test_node_builder(self):
        g = create_graph()
        node = g.node("person").id("N99").meta(name="Bob").content("Bob content").add()
        assert node.id == "N99"
        assert node.type == "person"
        assert node.meta["name"] == "Bob"

    def test_node_builder_context(self):
        g = create_graph()
        with g.node("person").id("N100") as node:
            node.content = "Context content"
            node.meta["role"] = "admin"
        assert g.has_node("N100")
        assert g.get_node("N100").content == "Context content"

    def test_get_node(self):
        g = create_graph()
        g.add_node("person", id_="N1")
        assert g.get_node("N1") is not None
        assert g.get_node("N999") is None

    def test_has_node(self):
        g = create_graph()
        g.add_node("person", id_="N1")
        assert g.has_node("N1")
        assert not g.has_node("N999")

    def test_remove_node(self):
        g = create_graph()
        g.add_node("person", id_="N1")
        g.add_node("person", id_="N2")
        g.add_edge("N1", "N2", "knows")
        removed = g.remove_node("N1")
        assert removed.id == "N1"
        assert not g.has_node("N1")
        assert len(g.edges) == 0  # Edge should be removed too


class TestGraphDocumentEdges:
    """Test edge operations."""

    def test_add_edge(self):
        g = create_graph()
        g.add_node("person", id_="N1")
        g.add_node("person", id_="N2")
        edge = g.add_edge("N1", "N2", "knows", weight="5")
        assert edge.id == "E1"
        assert edge.from_id == "N1"
        assert edge.to_id == "N2"
        assert edge.rel == "knows"
        assert edge.meta["weight"] == "5"

    def test_edge_builder(self):
        g = create_graph()
        g.add_node("person", id_="N1")
        g.add_node("person", id_="N2")
        edge = g.edge("N1", "N2", "knows").meta(since="2020").add()
        assert edge.rel == "knows"
        assert edge.meta["since"] == "2020"

    def test_get_edge(self):
        g = create_graph()
        g.add_node("person", id_="N1")
        g.add_node("person", id_="N2")
        g.add_edge("N1", "N2", "knows", id_="E1")
        assert g.get_edge("E1") is not None
        assert g.get_edge("E999") is None

    def test_get_edges_from(self):
        g = create_graph()
        g.add_node("person", id_="N1")
        g.add_node("person", id_="N2")
        g.add_node("person", id_="N3")
        g.add_edge("N1", "N2", "knows")
        g.add_edge("N1", "N3", "knows")
        g.add_edge("N2", "N3", "knows")
        edges = g.get_edges_from("N1")
        assert len(edges) == 2

    def test_get_edges_to(self):
        g = create_graph()
        g.add_node("person", id_="N1")
        g.add_node("person", id_="N2")
        g.add_node("person", id_="N3")
        g.add_edge("N1", "N3", "knows")
        g.add_edge("N2", "N3", "knows")
        edges = g.get_edges_to("N3")
        assert len(edges) == 2

    def test_remove_edge(self):
        g = create_graph()
        g.add_node("person", id_="N1")
        g.add_node("person", id_="N2")
        g.add_edge("N1", "N2", "knows", id_="E1")
        g.remove_edge("E1")
        assert g.get_edge("E1") is None
        assert len(g.edges) == 0


class TestTierComputation:
    """Test tier computation (BFS)."""

    def test_single_node(self):
        g = create_graph()
        g.add_node("person", id_="N1")
        tiers = g._compute_tiers("N1", radius=1)
        assert tiers == {"N1": 0}

    def test_linear_chain(self):
        g = create_graph()
        g.add_node("person", id_="N1")
        g.add_node("person", id_="N2")
        g.add_node("person", id_="N3")
        g.add_edge("N1", "N2", "next")
        g.add_edge("N2", "N3", "next")
        tiers = g._compute_tiers("N1", radius=2)
        assert tiers == {"N1": 0, "N2": 1, "N3": 2}

    def test_radius_limit(self):
        g = create_graph()
        g.add_node("person", id_="N1")
        g.add_node("person", id_="N2")
        g.add_node("person", id_="N3")
        g.add_edge("N1", "N2", "next")
        g.add_edge("N2", "N3", "next")
        tiers = g._compute_tiers("N1", radius=1)
        assert tiers == {"N1": 0, "N2": 1}
        assert "N3" not in tiers

    def test_bidirectional_edges(self):
        g = create_graph()
        g.add_node("person", id_="N1")
        g.add_node("person", id_="N2")
        g.add_edge("N1", "N2", "knows")
        tiers_from_n1 = g._compute_tiers("N1", radius=1)
        tiers_from_n2 = g._compute_tiers("N2", radius=1)
        assert tiers_from_n1 == {"N1": 0, "N2": 1}
        assert tiers_from_n2 == {"N2": 0, "N1": 1}

    def test_focus_not_found(self):
        g = create_graph()
        with pytest.raises(NodeNotFoundError):
            g._compute_tiers("N999", radius=1)


class TestInOutFilling:
    """Test in_edges/out_edges auto-fill."""

    def test_fill_in_out_edges(self):
        g = create_graph()
        g.add_node("person", id_="N1")
        g.add_node("person", id_="N2")
        g.add_node("person", id_="N3")
        g.add_edge("N1", "N2", "knows")
        g.add_edge("N2", "N3", "knows")
        g._fill_in_out_edges({"N1", "N2", "N3"})
        n1 = g.get_node("N1")
        n2 = g.get_node("N2")
        n3 = g.get_node("N3")
        assert n1.out_edges == ["N2:knows"]
        assert n1.in_edges == []
        assert n2.out_edges == ["N3:knows"]
        assert n2.in_edges == ["N1:knows"]
        assert n3.out_edges == []
        assert n3.in_edges == ["N2:knows"]

    def test_fill_partial_set(self):
        g = create_graph()
        g.add_node("person", id_="N1")
        g.add_node("person", id_="N2")
        g.add_node("person", id_="N3")
        g.add_edge("N1", "N2", "knows")
        g.add_edge("N2", "N3", "knows")
        g._fill_in_out_edges({"N1", "N2"})
        n1 = g.get_node("N1")
        n2 = g.get_node("N2")
        assert n1.out_edges == ["N2:knows"]
        assert n2.in_edges == ["N1:knows"]
        assert n2.out_edges == []  # N3 not in set


class TestTiersString:
    """Test tiers string building."""

    def test_build_tiers_string(self):
        g = create_graph()
        tiers = {"N1": 0, "N2": 1, "N3": 1}
        result = g._build_tiers_string(tiers)
        assert "0: N1" in result
        assert "1:" in result
        assert "N2" in result
        assert "N3" in result

    def test_build_tiers_string_sorted(self):
        g = create_graph()
        tiers = {"N3": 2, "N1": 0, "N2": 1}
        result = g._build_tiers_string(tiers)
        lines = result.split("\n")
        assert lines[0].startswith("0:")
        assert lines[1].startswith("1:")
        assert lines[2].startswith("2:")


class TestGraphRender:
    """Test graph rendering."""

    def test_render_without_focus(self):
        g = create_graph()
        g.add_node("person", "Alice", id_="N1")
        g.add_node("person", "Bob", id_="N2")
        g.add_edge("N1", "N2", "knows")
        output = g.render()
        assert "@node N1 person" in output
        assert "@node N2 person" in output
        assert "@edge E1 N1 -> N2 knows" in output

    def test_render_with_focus(self):
        g = create_graph()
        g.add_node("person", "Alice", id_="N1")
        g.add_node("person", "Bob", id_="N2")
        g.add_node("person", "Carol", id_="N3")
        g.add_edge("N1", "N2", "knows")
        g.add_edge("N2", "N3", "knows")
        output = g.render(focus="N1", radius=1)
        assert "@ctx" in output
        assert "@node N1 person" in output
        assert "@node N2 person" in output
        assert "N3" not in output  # Outside radius

    def test_render_focus_last(self):
        g = create_graph()
        g.add_node("person", id_="N1")
        g.add_node("person", id_="N2")
        g.add_edge("N1", "N2", "knows")
        output = g.render(focus="N1", radius=1, order="focus_last")
        lines = output.split("\n")
        ctx_line = next(i for i, line in enumerate(lines) if "@ctx" in line)
        focus_line = next(i for i, line in enumerate(lines) if "@node N1" in line)
        assert ctx_line < focus_line  # ctx before focus

    def test_render_focus_first(self):
        g = create_graph()
        g.add_node("person", id_="N1")
        g.add_node("person", id_="N2")
        g.add_edge("N1", "N2", "knows")
        output = g.render(focus="N1", radius=1, order="focus_first")
        lines = output.split("\n")
        ctx_idx = next(i for i, line in enumerate(lines) if "@ctx" in line)
        focus_idx = next(i for i, line in enumerate(lines) if "@node N1" in line)
        n2_idx = next(i for i, line in enumerate(lines) if "@node N2" in line)
        assert ctx_idx < focus_idx < n2_idx

    def test_render_with_ctx_content(self):
        g = create_graph()
        g.add_node("person", id_="N1")
        output = g.render(focus="N1", radius=0, ctx_content="Context info")
        assert "Context info" in output

    def test_render_edge_hidden(self):
        g = create_graph()
        g.add_node("person", id_="N1")
        g.add_node("person", id_="N2")
        g.add_edge("N1", "N2", "knows", render_edge=False)
        output = g.render(focus="N1", radius=1)
        assert "@edge" not in output

    def test_render_prefix_suffix(self):
        g = create_graph()
        g.prefix = "# Graph Document"
        g.suffix = "# End"
        g.add_node("person", id_="N1")
        output = g.render(focus="N1", radius=0)
        assert output.startswith("# Graph Document")
        assert output.endswith("# End")


class TestGraphRenderAsync:
    """Test async graph rendering."""

    @pytest.mark.asyncio
    async def test_render_async_without_focus(self):
        g = create_graph()
        g.add_node("person", "Alice", id_="N1")
        g.add_node("person", "Bob", id_="N2")
        g.add_edge("N1", "N2", "knows")
        output = await g.arender()
        assert "@node N1 person" in output
        assert "@node N2 person" in output
        assert "@edge E1 N1 -> N2 knows" in output

    @pytest.mark.asyncio
    async def test_render_async_with_focus(self):
        g = create_graph()
        g.add_node("person", "Alice", id_="N1")
        g.add_node("person", "Bob", id_="N2")
        g.add_edge("N1", "N2", "knows")
        output = await g.arender(focus="N1", radius=1)
        assert "@ctx" in output
        assert "@node N1 person" in output
        assert "@node N2 person" in output


class TestSorterStrategies:
    """Test different sorting strategies."""

    def test_tier_asc(self):
        g = create_graph()
        g.add_node("person", id_="N1")
        g.add_node("person", id_="N2")
        g.add_node("person", id_="N3")
        g.add_edge("N1", "N2", "next")
        g.add_edge("N2", "N3", "next")
        output = g.render(focus="N1", radius=2, order="tier_asc")
        lines = output.split("\n")
        n1_idx = next(i for i, line in enumerate(lines) if "@node N1" in line)
        n2_idx = next(i for i, line in enumerate(lines) if "@node N2" in line)
        n3_idx = next(i for i, line in enumerate(lines) if "@node N3" in line)
        assert n1_idx < n2_idx < n3_idx

    def test_tier_desc(self):
        g = create_graph()
        g.add_node("person", id_="N1")
        g.add_node("person", id_="N2")
        g.add_node("person", id_="N3")
        g.add_edge("N1", "N2", "next")
        g.add_edge("N2", "N3", "next")
        output = g.render(focus="N1", radius=2, order="tier_desc")
        lines = output.split("\n")
        n1_idx = next(i for i, line in enumerate(lines) if "@node N1" in line)
        n2_idx = next(i for i, line in enumerate(lines) if "@node N2" in line)
        n3_idx = next(i for i, line in enumerate(lines) if "@node N3" in line)
        assert n3_idx < n2_idx < n1_idx


class TestDuplicateID:
    """Test duplicate ID handling."""

    def test_duplicate_node_id(self):
        from llb_doc.core.document import DuplicateIDError

        g = create_graph()
        g.add_node("person", id_="N1")
        with pytest.raises(DuplicateIDError):
            g.add_node("person", id_="N1")


class TestNode:
    """Test Node block rendering and properties."""

    def test_render_header(self) -> None:
        node = Node(id="N1", type="person")
        assert node.render_header() == "@node N1 person"

    def test_render_header_with_lang(self) -> None:
        node = Node(id="N2", type="code", lang="python")
        assert node.render_header() == "@node N2 code python"

    def test_render_full(self) -> None:
        node = Node(id="N1", type="person", content="Alice")
        result = node.render()
        assert "@node N1 person" in result
        assert "Alice" in result
        assert "@end N1" in result

    def test_tier_and_edges(self) -> None:
        node = Node(id="N1", type="person")
        node.tier = 0
        node.in_edges = ["N2:knows"]
        node.out_edges = ["N3:likes"]
        assert node.tier == 0
        assert node.in_edges == ["N2:knows"]
        assert node.out_edges == ["N3:likes"]

    def test_meta_access(self) -> None:
        node = Node(id="N1", type="person", name="Alice")
        assert node.name == "Alice"


class TestEdge:
    """Test Edge block rendering and properties."""

    def test_render_header(self) -> None:
        edge = Edge(id="E1", from_id="N1", to_id="N2", rel="knows")
        assert edge.render_header() == "@edge E1 N1 -> N2 knows"

    def test_render_header_with_lang(self) -> None:
        edge = Edge(id="E2", from_id="N1", to_id="N2", rel="refs", lang="json")
        assert edge.render_header() == "@edge E2 N1 -> N2 refs json"

    def test_render_full(self) -> None:
        edge = Edge(id="E1", from_id="N1", to_id="N2", rel="knows", content="since 2020")
        result = edge.render()
        assert "@edge E1 N1 -> N2 knows" in result
        assert "since 2020" in result
        assert "@end E1" in result

    def test_render_edge_flag(self) -> None:
        edge = Edge(id="E1", from_id="N1", to_id="N2", rel="knows", render_edge=False)
        assert edge.render_edge is False


class TestCtx:
    """Test Ctx block rendering and properties."""

    def test_render_header(self) -> None:
        ctx = Ctx(id="C1")
        assert ctx.render_header() == "@ctx C1"

    def test_render_full(self) -> None:
        ctx = Ctx(id="C1", content="context info")
        result = ctx.render()
        assert "@ctx C1" in result
        assert "context info" in result
        assert "@end C1" in result

    def test_focus_and_radius(self) -> None:
        ctx = Ctx(id="C1", focus="N42", radius=2, strategy="bfs", tiers="0:N42;1:N10")
        assert ctx.focus == "N42"
        assert ctx.radius == 2
        assert ctx.strategy == "bfs"
        assert ctx.tiers == "0:N42;1:N10"


class TestRenderFree:
    """Test render_free() free mode rendering."""

    def test_render_free_basic(self):
        """Test basic render_free with node IDs only."""
        g = create_graph()
        g.add_node("person", "Alice content", id_="N1")
        g.add_node("person", "Bob content", id_="N2")
        g.add_node("person", "Carol content", id_="N3")
        g.add_edge("N1", "N2", "knows", id_="E1")
        g.add_edge("N2", "N3", "knows", id_="E2")

        output = g.render_free(items=["N1", "E1", "N2"])

        assert "@node N1 person" in output
        assert "@node N2 person" in output
        assert "@edge E1 N1 -> N2 knows" in output
        assert "Alice content" in output
        assert "Bob content" in output
        # N3 and E2 should not be in output
        assert "@node N3" not in output
        assert "@edge E2" not in output

    def test_render_free_with_order(self):
        """Test that render_free respects the order of items."""
        g = create_graph()
        g.add_node("person", "Alice", id_="N1")
        g.add_node("person", "Bob", id_="N2")
        g.add_edge("N1", "N2", "knows", id_="E1")

        output = g.render_free(items=["N2", "E1", "N1"])
        lines = output.split("\n")

        n1_idx = next(i for i, line in enumerate(lines) if "@node N1" in line)
        n2_idx = next(i for i, line in enumerate(lines) if "@node N2" in line)
        e1_idx = next(i for i, line in enumerate(lines) if "@edge E1" in line)

        # Order should be N2 -> E1 -> N1
        assert n2_idx < e1_idx < n1_idx

    def test_render_free_with_brief(self):
        """Test render_free with brief mode (tuple syntax)."""
        g = create_graph()
        g.add_node("person", "Alice long content here", id_="N1")
        g.add_node("person", "Bob long content here", id_="N2")
        g.add_edge("N1", "N2", "knows", id_="E1", content="Edge content")

        output = g.render_free(items=[
            "N1",           # full render
            ("N2", True),   # brief render
            ("E1", True),   # brief render
        ])

        # N1 should have full content
        assert "Alice long content here" in output

        # N2 should be brief (no content)
        assert "@node N2 person" in output
        assert "Bob long content here" not in output

        # E1 should be brief (no content)
        assert "@edge E1 N1 -> N2 knows" in output
        assert "Edge content" not in output

    def test_render_free_with_ctx_dict(self):
        """Test render_free with ctx as dict."""
        g = create_graph()
        g.add_node("person", "Alice", id_="N1")

        output = g.render_free(
            items=["N1"],
            ctx={
                "content": "Custom context content",
                "meta": {"view": "neighborhood", "roots": "N1"},
            },
        )

        assert "@ctx" in output
        assert "Custom context content" in output
        assert "view=neighborhood" in output
        assert "roots=N1" in output

        # ctx should come before N1
        lines = output.split("\n")
        ctx_idx = next(i for i, line in enumerate(lines) if "@ctx" in line)
        n1_idx = next(i for i, line in enumerate(lines) if "@node N1" in line)
        assert ctx_idx < n1_idx

    def test_render_free_with_ctx_object(self):
        """Test render_free with ctx as Ctx object."""
        g = create_graph()
        g.add_node("person", "Alice", id_="N1")

        ctx = Ctx(id="custom-ctx", content="My context", meta={"mode": "custom"})
        output = g.render_free(items=["N1"], ctx=ctx)

        assert "@ctx custom-ctx" in output
        assert "My context" in output
        assert "mode=custom" in output

    def test_render_free_without_ctx(self):
        """Test render_free without ctx (ctx=None)."""
        g = create_graph()
        g.add_node("person", "Alice", id_="N1")

        output = g.render_free(items=["N1"], ctx=None)

        assert "@ctx" not in output
        assert "@node N1 person" in output

    def test_render_free_with_custom_brief_renderer(self):
        """Test render_free with custom brief_renderer function."""
        g = create_graph()
        g.add_node("person", "Alice content", id_="N1", name="Alice")
        g.add_node("person", "Bob content", id_="N2", name="Bob")

        def custom_brief(block):
            return f"[{block.type}:{block.id}]"

        output = g.render_free(
            items=["N1", ("N2", True)],
            brief_renderer=custom_brief,
        )

        # N1 should be full render
        assert "@node N1 person" in output
        assert "Alice content" in output

        # N2 should use custom brief renderer
        assert "[person:N2]" in output
        assert "Bob content" not in output

    def test_render_free_fills_in_out_edges(self):
        """Test that render_free correctly fills in_edges and out_edges."""
        g = create_graph()
        g.add_node("person", "Alice", id_="N1")
        g.add_node("person", "Bob", id_="N2")
        g.add_node("person", "Carol", id_="N3")
        g.add_edge("N1", "N2", "knows")
        g.add_edge("N2", "N3", "knows")

        # Only include N1 and N2
        output = g.render_free(items=["N1", "N2"])

        # Check that in_edges/out_edges are filled correctly
        assert "out_edges=['N2:knows']" in output
        assert "in_edges=['N1:knows']" in output
        # N3 is not included, so N2's out_edges to N3 should not appear
        assert "N3:knows" not in output

    def test_render_free_skips_unknown_ids(self):
        """Test that render_free skips unknown IDs gracefully."""
        g = create_graph()
        g.add_node("person", "Alice", id_="N1")

        # Include unknown ID - should be skipped
        output = g.render_free(items=["N1", "UNKNOWN", "N999"])

        assert "@node N1 person" in output
        # No error, unknown IDs are just skipped

    def test_render_free_with_prefix_suffix(self):
        """Test that render_free respects prefix and suffix."""
        g = create_graph()
        g.prefix = "# Graph Start"
        g.suffix = "# Graph End"
        g.add_node("person", "Alice", id_="N1")

        output = g.render_free(items=["N1"])

        assert output.startswith("# Graph Start")
        assert output.endswith("# Graph End")

    def test_render_free_empty_items(self):
        """Test render_free with empty items list."""
        g = create_graph()
        g.add_node("person", "Alice", id_="N1")

        output = g.render_free(items=[])

        # Should be empty (or just prefix/suffix if set)
        assert "@node" not in output

    def test_render_free_mixed_nodes_and_edges(self):
        """Test render_free with mixed nodes and edges in various orders."""
        g = create_graph()
        g.add_node("person", "A", id_="N1")
        g.add_node("person", "B", id_="N2")
        g.add_node("person", "C", id_="N3")
        g.add_edge("N1", "N2", "r1", id_="E1")
        g.add_edge("N2", "N3", "r2", id_="E2")

        output = g.render_free(items=["E1", "N2", "E2", "N1", "N3"])
        lines = output.split("\n")

        e1_idx = next(i for i, line in enumerate(lines) if "@edge E1" in line)
        n2_idx = next(i for i, line in enumerate(lines) if "@node N2" in line)
        e2_idx = next(i for i, line in enumerate(lines) if "@edge E2" in line)
        n1_idx = next(i for i, line in enumerate(lines) if "@node N1" in line)
        n3_idx = next(i for i, line in enumerate(lines) if "@node N3" in line)

        assert e1_idx < n2_idx < e2_idx < n1_idx < n3_idx


class TestRenderFreeAsync:
    """Test async version of render_free."""

    @pytest.mark.asyncio
    async def test_arender_free_basic(self):
        """Test basic async render_free."""
        g = create_graph()
        g.add_node("person", "Alice", id_="N1")
        g.add_node("person", "Bob", id_="N2")
        g.add_edge("N1", "N2", "knows", id_="E1")

        output = await g.arender_free(items=["N1", "E1", "N2"])

        assert "@node N1 person" in output
        assert "@node N2 person" in output
        assert "@edge E1 N1 -> N2 knows" in output

    @pytest.mark.asyncio
    async def test_arender_free_with_ctx(self):
        """Test async render_free with ctx."""
        g = create_graph()
        g.add_node("person", "Alice", id_="N1")

        output = await g.arender_free(
            items=["N1"],
            ctx={"content": "Async context"},
        )

        assert "@ctx" in output
        assert "Async context" in output


class TestBlockRenderBrief:
    """Test Block.render_brief() method."""

    def test_node_render_brief(self):
        """Test Node brief rendering (meta only, no content)."""
        node = Node(id="N1", type="person", content="Long content here")
        node.tier = 0
        node.in_edges = ["N2:knows"]
        node.out_edges = ["N3:likes"]
        node.meta["name"] = "Alice"

        result = node.render_brief()

        assert "@node N1 person" in result
        assert "tier=0" in result
        assert "in_edges=['N2:knows']" in result
        assert "out_edges=['N3:likes']" in result
        assert "name=Alice" in result
        assert "@end N1" in result
        # Content should NOT be present
        assert "Long content here" not in result

    def test_edge_render_brief(self):
        """Test Edge brief rendering (meta only, no content)."""
        edge = Edge(
            id="E1",
            from_id="N1",
            to_id="N2",
            rel="knows",
            content="Edge content here",
            weight="5",
        )

        result = edge.render_brief()

        assert "@edge E1 N1 -> N2 knows" in result
        assert "weight=5" in result
        assert "@end E1" in result
        # Content should NOT be present
        assert "Edge content here" not in result

    def test_ctx_render_brief(self):
        """Test Ctx brief rendering (meta only, no content)."""
        ctx = Ctx(
            id="C1",
            content="Context content here",
            focus="N1",
            radius=2,
        )
        ctx.meta["mode"] = "custom"

        result = ctx.render_brief()

        assert "@ctx C1" in result
        assert "focus=N1" in result
        assert "radius=2" in result
        assert "mode=custom" in result
        assert "@end C1" in result
        # Content should NOT be present
        assert "Context content here" not in result

    def test_render_brief_no_meta(self):
        """Test brief rendering with no meta (should use short form)."""
        from llb_doc.core.block import Block

        block = Block(id="B1", type="test")
        result = block.render_brief()

        assert result == "@block B1 test @end"
