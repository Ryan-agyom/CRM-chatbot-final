import { useEffect } from "react";

export function useSectionTitle(title) {
  useEffect(() => {
    document.title = title;
  }, [title]);
}
