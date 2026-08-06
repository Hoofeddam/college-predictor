(function () {
    "use strict";

    function el(tag, className, text) {
        var node = document.createElement(tag);

        if (className) {
            node.className = className;
        }

        if (text !== undefined && text !== null) {
            node.textContent = text;
        }

        return node;
    }

    function formatValue(value) {
        return value === null || value === undefined ? "—" : String(value);
    }

    function statCell(label, value, accent) {

        var cell = el("div");
        cell.appendChild(el("p", "stat-label", label));

        var valueEl = document.createElement("p");
        valueEl.className = "stat-value" + (accent ? " accent" : "");

        if (value instanceof Node) {
            valueEl.appendChild(value);
        } else {
            valueEl.textContent = formatValue(value);
        }

        cell.appendChild(valueEl);

        return cell;
    }

    function websiteLink(url) {

        if (!url) {
            return null;
        }

        var link = el("a", null, "Visit ↗");
        link.href = url;
        link.target = "_blank";
        link.rel = "noopener";

        return link;
    }

    function branchTitle(branch) {
        return (branch.college || "Unknown college") +
            (branch.branch ? " — " + branch.branch : "");
    }

    function viewDetailsLink(className, collegeId) {

        var link = el("a", "btn " + className, "View Details");

        if (collegeId) {
            link.href = "/college/" + collegeId;
        } else {
            link.setAttribute("aria-disabled", "true");
            link.classList.add("btn-disabled");
        }

        return link;
    }

    function renderComparisonCard(block) {

        var data = block.data || {};
        var branch1 = data.branch_1 || {};
        var branch2 = data.branch_2 || {};

        var card = el("div", "card block-card");
        card.setAttribute("role", "group");
        card.setAttribute(
            "aria-label",
            "Comparison of " + branchTitle(branch1) + " and " + branchTitle(branch2)
        );

        card.appendChild(el("p", "eyebrow", "Comparison"));

        var columns = el("div", "block-comparison-columns");

        [branch1, branch2].forEach(function (branch) {

            var column = el("div", "block-comparison-column");

            column.appendChild(el("h4", "result-college", branch.college || "Unknown college"));
            column.appendChild(el("p", "result-branch", branch.branch || ""));

            var primaryStats = el("div", "stat-grid");
            primaryStats.appendChild(statCell(
                "Avg Package",
                branch.avg_package != null ? branch.avg_package + " LPA" : null
            ));
            primaryStats.appendChild(statCell(
                "Placement Rate",
                branch.placement_rate != null ? branch.placement_rate + "%" : null
            ));
            primaryStats.appendChild(statCell("NIRF Rank", branch.nirf_rank));
            column.appendChild(primaryStats);

            var details = el("details", "block-details");
            details.appendChild(el("summary", null, "Fees & more"));

            var moreStats = el("div", "stat-grid");
            moreStats.appendChild(statCell(
                "Median Package",
                branch.median_package != null ? branch.median_package + " LPA" : null
            ));
            moreStats.appendChild(statCell(
                "Fees",
                branch.fees != null ? "₹" + branch.fees : null
            ));
            moreStats.appendChild(statCell(
                "Hostel Fees",
                branch.hostel_fees != null ? "₹" + branch.hostel_fees : null
            ));
            moreStats.appendChild(statCell("Official Website", websiteLink(branch.website)));
            details.appendChild(moreStats);

            column.appendChild(details);

            columns.appendChild(column);
        });

        card.appendChild(columns);

        var footer = el("div", "result-foot");
        footer.appendChild(viewDetailsLink("btn-secondary", branch1.college_id));
        footer.appendChild(viewDetailsLink("btn-ghost", branch2.college_id));
        card.appendChild(footer);

        return card;
    }

    function renderRecommendationCard(block) {

        var data = block.data || {};

        var card = el("div", "card block-card");
        card.setAttribute("role", "group");
        card.setAttribute(
            "aria-label",
            (data.college_name || "College") +
                (data.branch ? ", " + data.branch : "") +
                " recommendation"
        );

        var top = el("div", "result-top");
        var titleWrap = el("div");
        titleWrap.appendChild(el("h4", "result-college", data.college_name || "Unknown college"));
        titleWrap.appendChild(el("p", "result-branch", data.branch || ""));
        top.appendChild(titleWrap);
        card.appendChild(top);

        var primaryStats = el("div", "stat-grid");
        primaryStats.appendChild(statCell("Closing Rank", data.closing_rank, true));
        primaryStats.appendChild(statCell(
            "Avg Package",
            data.avg_package != null ? data.avg_package + " LPA" : null
        ));
        primaryStats.appendChild(statCell(
            "Placement Rate",
            data.placement_rate != null ? data.placement_rate + "%" : null
        ));
        primaryStats.appendChild(statCell("NIRF Rank", data.nirf_rank));
        card.appendChild(primaryStats);

        var details = el("details", "block-details");
        details.appendChild(el("summary", null, "Fees & more"));

        var moreStats = el("div", "stat-grid");
        moreStats.appendChild(statCell(
            "Fees",
            data.fees != null ? "₹" + data.fees : null
        ));
        moreStats.appendChild(statCell(
            "Hostel Fees",
            data.hostel_fees != null ? "₹" + data.hostel_fees : null
        ));
        moreStats.appendChild(statCell("Official Website", websiteLink(data.website)));
        details.appendChild(moreStats);

        card.appendChild(details);

        var footer = el("div", "result-foot");

        var compare = el("a", "btn btn-ghost", "Compare");
        compare.href = "/compare";

        footer.appendChild(viewDetailsLink("btn-secondary", data.college_id));
        footer.appendChild(compare);
        card.appendChild(footer);

        return card;
    }

    function resultTag(className, text) {
        return text ? el("span", "tag" + (className ? " " + className : ""), text) : null;
    }

    function renderPredictionCard(block) {

        var data = block.data || {};

        var card = el("div", "card block-card");
        card.setAttribute("role", "group");
        card.setAttribute(
            "aria-label",
            (data.college_name || "College") +
                (data.branch ? ", " + data.branch : "") +
                " — eligible"
        );

        var top = el("div", "result-top");

        var titleWrap = el("div");
        titleWrap.appendChild(el("h4", "result-college", data.college_name || "Unknown college"));
        titleWrap.appendChild(el("p", "result-branch", data.branch || ""));
        top.appendChild(titleWrap);

        var tags = el("div", "result-tags");
        [
            resultTag(null, data.exam),
            resultTag(null, [data.category, data.quota].filter(Boolean).join(" · ")),
            resultTag("tag-brass", data.nirf_rank ? "NIRF #" + data.nirf_rank : null)
        ].forEach(function (tag) {
            if (tag) {
                tags.appendChild(tag);
            }
        });
        top.appendChild(tags);

        card.appendChild(top);

        var primaryStats = el("div", "stat-grid");
        primaryStats.appendChild(statCell("Closing Rank", data.closing_rank, true));
        primaryStats.appendChild(statCell(
            "Avg Package",
            data.avg_package != null ? data.avg_package + " LPA" : null
        ));
        primaryStats.appendChild(statCell(
            "Median Package",
            data.median_package != null ? data.median_package + " LPA" : null
        ));
        primaryStats.appendChild(statCell(
            "Placement Rate",
            data.placement_rate != null ? data.placement_rate + "%" : null
        ));
        card.appendChild(primaryStats);

        var details = el("details", "block-details");
        details.appendChild(el("summary", null, "Fees & more"));

        var moreStats = el("div", "stat-grid");
        moreStats.appendChild(statCell(
            "Fees",
            data.fees != null ? "₹" + data.fees : null
        ));
        moreStats.appendChild(statCell(
            "Hostel Fees",
            data.hostel_fees != null ? "₹" + data.hostel_fees : null
        ));
        moreStats.appendChild(statCell("Official Website", websiteLink(data.website)));
        details.appendChild(moreStats);

        card.appendChild(details);

        var footer = el("div", "result-foot");
        var compare = el("a", "btn btn-ghost", "Compare");
        compare.href = "/compare";

        footer.appendChild(viewDetailsLink("btn-secondary", data.college_id));
        footer.appendChild(compare);
        card.appendChild(footer);

        return card;
    }

    // Frontend mirror of response_blocks.BLOCK_BUILDERS on the backend.
    // Adding a new block type later means adding one renderer function
    // and one line here — nothing else in chat.js needs to change.
    var BLOCK_RENDERERS = {
        comparison_card: renderComparisonCard,
        recommendation_card: renderRecommendationCard,
        prediction_card: renderPredictionCard
    };

    function renderBlock(block) {

        if (!block || !block.type) {
            return null;
        }

        var renderer = BLOCK_RENDERERS[block.type];

        if (!renderer) {
            return null;
        }

        try {
            return renderer(block);
        } catch (err) {
            return null;
        }
    }

    function renderBlocks(blocks) {

        var fragment = document.createDocumentFragment();

        (blocks || []).forEach(function (block) {

            var node = renderBlock(block);

            if (node) {
                fragment.appendChild(node);
            }
        });

        return fragment;
    }

    window.BlockRenderer = {
        renderBlocks: renderBlocks
    };
})();
