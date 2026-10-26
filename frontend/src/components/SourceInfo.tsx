export default function SourceInfo({ name, url, importedAt }: {
  name?: string | null; url?: string | null; importedAt?: string | null;
}) {
  if (!url) return null;
  return <div className="text-xs text-muted-foreground mt-1">
    <a href={url} target="_blank" rel="noopener noreferrer" className="text-primary underline underline-offset-2">
      {name || '查看原始来源'} ↗
    </a>
    {importedAt && <span className="ml-2">采集于 {new Date(importedAt).toLocaleDateString('zh-CN')}</span>}
  </div>;
}
