import { createNativeStackNavigator } from "@react-navigation/native-stack";

import { headerScreenOptions } from "../../constants/navigationTheme";
import { PredictorStackParamList } from "../../navigation/types";
import { PredictorFormScreen } from "./screens/PredictorFormScreen";
import { PredictorResultsScreen } from "./screens/PredictorResultsScreen";

const Stack = createNativeStackNavigator<PredictorStackParamList>();

// Form -> Results is a strictly sequential push, not two screens needing
// simultaneous access to shared state -- results travel as navigation
// params (see PredictorResultsScreen), so this navigator needs no local
// state of its own, same shape as ProfileNavigator.
export function PredictorNavigator() {
  return (
    <Stack.Navigator screenOptions={headerScreenOptions}>
      <Stack.Screen name="PredictorForm" component={PredictorFormScreen} options={{ title: "Predictor" }} />
      <Stack.Screen
        name="PredictorResults"
        component={PredictorResultsScreen}
        options={{ title: "Eligible Colleges" }}
      />
    </Stack.Navigator>
  );
}
