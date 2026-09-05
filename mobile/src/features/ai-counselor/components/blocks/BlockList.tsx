import { ComponentType } from "react";
import { StyleSheet, View } from "react-native";

import { ResponseBlock } from "../../../../api/ai";
import { ComparisonCard } from "./ComparisonCard";
import { PredictionCard } from "./PredictionCard";
import { RecommendationCard } from "./RecommendationCard";

const SUPPORTED_VERSION = 1;

// Mirrors static/js/blocks.js's BLOCK_RENDERERS map. Adding a new block
// type later means adding one component and one line here.
const BLOCK_RENDERERS: Record<string, ComponentType<{ block: ResponseBlock }>> = {
  recommendation_card: RecommendationCard,
  prediction_card: PredictionCard,
  comparison_card: ComparisonCard,
};

// The forward-compatibility contract lives here, centrally -- not in the
// individual card components, which can assume they only ever receive a
// supported, valid block. Three independent reasons to skip a block:
// unrecognized type, a version newer than this client understands, or
// data that's missing outright (a floor beneath the per-card type
// assertions, which don't runtime-check beyond this).
function renderBlock(block: ResponseBlock, key: string) {
  const Renderer = BLOCK_RENDERERS[block.type];

  if (!Renderer || block.version > SUPPORTED_VERSION || !block.data) {
    return null;
  }

  return <Renderer key={key} block={block} />;
}

export function BlockList({ blocks }: { blocks: ResponseBlock[] }) {
  return (
    <View style={styles.list}>
      {blocks.map((block, index) => renderBlock(block, `${block.type}-${index}`))}
    </View>
  );
}

const styles = StyleSheet.create({
  list: {
    gap: 10,
    marginTop: 8,
  },
});
