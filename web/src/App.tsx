import { BrowserRouter, Routes, Route } from "react-router-dom"
import { AuthProvider } from "@/contexts/AuthContext"
import { AppLayout } from "@/components/AppLayout"
import LoginPage from "@/pages/LoginPage"
import RepoSelector from "@/pages/RepoSelector"
import SearchResults from "@/pages/SearchResults"
import IssueList from "@/pages/IssueList"
import NewIssue from "@/pages/NewIssue"
import IssueDetail from "@/pages/IssueDetail"
import NotFound from "@/pages/NotFound"

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route element={<AppLayout />}>
            <Route index element={<RepoSelector />} />
            <Route path="search" element={<SearchResults />} />
            <Route path=":owner/:repo/issues" element={<IssueList />} />
            <Route path=":owner/:repo/issues/new" element={<NewIssue />} />
            <Route path=":owner/:repo/issues/:number" element={<IssueDetail />} />
            <Route path="*" element={<NotFound />} />
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App
