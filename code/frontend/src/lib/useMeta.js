import { useEffect } from 'react';

/**
 * tiny hook to update page title and description meta tag
 * @param {{title?: string, description?: string}} opts
 */
export default function useMeta({ title, description } = {}) {
  useEffect(() => {
    if (title) document.title = `${title} — remAIke.TV`;
    if (description) {
      let meta = document.querySelector('meta[name="description"]');
      if (!meta) {
        meta = document.createElement('meta');
        meta.name = 'description';
        document.head.appendChild(meta);
      }
      meta.content = description;
    }
  }, [title, description]);
}
