import { Navbar } from "./components";
import { Route, Routes } from "react-router";
import { BooksPage, BookPage, HomePage } from "./pages";

function App() {
  return (
    <div>
      <Navbar />
      <Routes>
        <Route path="" element={<HomePage />} />

        <Route path="/book">
          <Route path="" element={<BooksPage />} />
          <Route path=":bookId" element={<BookPage />} />
        </Route>
      </Routes>
    </div>
  );
}

export default App;
