import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { useState } from "react";

import { ComparisonBranch } from "../../api/comparison";
import { headerScreenOptions } from "../../constants/navigationTheme";
import { ComparisonStackParamList } from "../../navigation/types";
import { BranchPickerScreen } from "./screens/BranchPickerScreen";
import { ComparisonFormScreen } from "./screens/ComparisonFormScreen";
import { ComparisonResultsScreen } from "./screens/ComparisonResultsScreen";

const Stack = createNativeStackNavigator<ComparisonStackParamList>();

// branch1/branch2 lifted here, not left local to ComparisonFormScreen,
// because BranchPickerScreen needs to write a value back to a screen
// that's still mounted underneath it in the stack -- the same "return a
// value to an already-open sibling" relationship AiCounselorNavigator has
// between its drawer content and ChatScreen. Passing a value *back* to an
// existing screen doesn't fit React Navigation's forward-only params
// idiom the way Predictor's one-way Form -> Results hand-off did, so this
// reuses the already-proven lifted-state pattern instead of fighting it.
export function ComparisonNavigator() {
  const [branch1, setBranch1] = useState<ComparisonBranch | null>(null);
  const [branch2, setBranch2] = useState<ComparisonBranch | null>(null);

  // Plain exchange of the two lifted values -- no network request, no
  // other state touched.
  function handleSwap() {
    setBranch1(branch2);
    setBranch2(branch1);
  }

  return (
    <Stack.Navigator screenOptions={headerScreenOptions}>
      <Stack.Screen name="ComparisonForm" options={{ title: "Compare" }}>
        {({ navigation }) => (
          <ComparisonFormScreen
            navigation={navigation}
            branch1={branch1}
            branch2={branch2}
            onSwap={handleSwap}
          />
        )}
      </Stack.Screen>
      <Stack.Screen name="BranchPicker" options={{ title: "Select a Branch" }}>
        {({ route }) => (
          <BranchPickerScreen
            excludeBranchId={route.params.target === "branch1" ? branch2?.id : branch1?.id}
            onSelect={route.params.target === "branch1" ? setBranch1 : setBranch2}
          />
        )}
      </Stack.Screen>
      <Stack.Screen
        name="ComparisonResults"
        component={ComparisonResultsScreen}
        options={{ title: "Comparison" }}
      />
    </Stack.Navigator>
  );
}
