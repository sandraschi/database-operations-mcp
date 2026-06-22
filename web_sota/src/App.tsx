import {
  Navigate,
  Route,
  BrowserRouter as Router,
  Routes,
} from "react-router-dom";
import { AppLayout } from "@/components/layout/app-layout";
import { Chat } from "@/pages/chat";
import { ConnectionManager } from "@/pages/connection-manager";
import { ConnectionWizard } from "@/pages/connection-wizard";
import { Connections } from "@/pages/connections";
import { Dashboard } from "@/pages/dashboard";
import { Data } from "@/pages/data";
import { DatabaseTypesHelp } from "@/pages/database-types-help";
import { ExportImport } from "@/pages/export-import";
import { GettingStarted } from "@/pages/getting-started";
import { Health } from "@/pages/health";
import { JobsExports } from "@/pages/jobs-exports";
import { LogsPage } from "@/pages/logs";
import { McpCapabilities } from "@/pages/mcp-capabilities";
import { Playground } from "@/pages/playground";
import { Schema } from "@/pages/schema";
import { SearchHub } from "@/pages/search-hub";
import { Settings } from "@/pages/settings";
import { SimpleQuery } from "@/pages/simple-query";
import { TableViewer } from "@/pages/table-viewer";
import { ToolExplorer } from "@/pages/tool-explorer";
import { Tools } from "@/pages/tools";

function App() {
  return (
    <Router>
      <AppLayout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/getting-started" element={<GettingStarted />} />
          <Route path="/database-types-help" element={<DatabaseTypesHelp />} />
          <Route path="/connection-wizard" element={<ConnectionWizard />} />
          <Route path="/connections" element={<Connections />} />
          <Route path="/schema" element={<Schema />} />
          <Route path="/table-viewer" element={<TableViewer />} />
          <Route path="/simple-query" element={<SimpleQuery />} />
          <Route path="/data" element={<Data />} />
          <Route path="/export-import" element={<ExportImport />} />
          <Route path="/health" element={<Health />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/tools" element={<Tools />} />
          <Route path="/tool-explorer" element={<ToolExplorer />} />
          <Route path="/playground" element={<Playground />} />
          <Route path="/search-hub" element={<SearchHub />} />
          <Route path="/jobs-exports" element={<JobsExports />} />
          <Route path="/mcp-capabilities" element={<McpCapabilities />} />
          <Route path="/connection-manager" element={<ConnectionManager />} />
          <Route path="/logs" element={<LogsPage />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AppLayout>
    </Router>
  );
}

export default App;
