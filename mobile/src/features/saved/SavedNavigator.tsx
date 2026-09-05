import { createNativeStackNavigator } from "@react-navigation/native-stack";

import { headerScreenOptions } from "../../constants/navigationTheme";
import { SavedStackParamList } from "../../navigation/types";
import { SavedCollegesScreen } from "./screens/SavedCollegesScreen";

const Stack = createNativeStackNavigator<SavedStackParamList>();

// No local state here -- CollegeDetail (reached via the root
// AuthenticatedStack, not registered in this stack) is the only mutation
// point; this navigator just hosts the list screen.
export function SavedNavigator() {
  return (
    <Stack.Navigator screenOptions={headerScreenOptions}>
      <Stack.Screen name="SavedCollegesList" component={SavedCollegesScreen} options={{ title: "Saved" }} />
    </Stack.Navigator>
  );
}
