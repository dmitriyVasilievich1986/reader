/**
 * Application store entry point: re-exports the main Zustand hook so imports can use `store` without reaching into slice folders.
 */

import { useMainStore } from "./main";

export { useMainStore };
