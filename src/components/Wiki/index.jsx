import React, {useRef, useState} from 'react';
import Link from '@docusaurus/Link';
import useBaseUrl from '@docusaurus/useBaseUrl';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import {ArrowUpRight, Compass, Swords, Settings2, Map, ExternalLink, ZoomIn, X, Play, Download} from 'lucide-react';

export function ModIdentity() {
  const {siteConfig: {customFields: {profile}}} = useDocusaurusContext();
  return <div className="mod-identity">
    <div className="mod-mark"><Swords size={22}/></div>
    <div><strong>{profile.name}</strong><span>{profile.game}</span></div>
  </div>;
}

export function SidebarLinks() {
  const {siteConfig: {customFields: {profile}}} = useDocusaurusContext();
  return <div className="sidebar-links">
    <Link href={profile.installationUrl}><Download size={15}/> Zainstaluj modyfikację <ArrowUpRight size={14}/></Link>
    <Link href="https://sefaris.eu">Wróć do Sefaris <ArrowUpRight size={14}/></Link>
    {profile.prototype && <span className="prototype-label">Podgląd wzoru wiki</span>}
  </div>;
}

export function HomeHeader({title}) {
  const {siteConfig: {customFields: {profile}}} = useDocusaurusContext();
  const background = useBaseUrl(profile.heroImage);
  return <header className="wiki-hero wiki-home-header" style={{backgroundImage: `linear-gradient(90deg, rgba(15,18,13,.94) 0%, rgba(15,18,13,.73) 42%, rgba(15,18,13,.18) 100%), url("${background}")`}}>
    <span className="eyebrow"><span className="tiny-rule"/> Sefaris Wiki</span>
    <h1 id="wiki-title">{title}</h1>
    {profile.heroDescription && <p className="wiki-home-description">{profile.heroDescription}</p>}
  </header>;
}

const shortcuts = [
  {icon: Compass, title: 'Pierwsze kroki', text: 'Zanim wyruszysz w drogę', url: '/pierwsze-kroki/'},
  {icon: Swords, title: 'Solucja', text: 'Zadania, wybory i konsekwencje', url: '/solucja/rozdzial-i/'},
  {icon: Settings2, title: 'Gothic.ini', text: 'Ustaw grę po swojemu', url: '/konfiguracja/'},
  {icon: Map, title: 'Mapy i sekrety', text: 'Znajdź to, czego szukasz', url: '/mapy/'},
];
export function QuickLinks() {
  return <div className="quick-links">{shortcuts.map(({icon: Icon, title, text, url}) => <Link to={url} className="quick-link" key={url}><Icon size={21}/><strong>{title}</strong><span>{text}</span><ArrowUpRight className="quick-arrow" size={16}/></Link>)}</div>;
}

export function ChapterLinks({chapters}) {
  return <div className="quick-links">{chapters.map(({title, text, url}, index) => <Link to={url} className="quick-link" key={url}><span className="chapter-number">{String(index + 1).padStart(2, '0')}</span><strong>{title}</strong><span>{text}</span><ArrowUpRight className="quick-arrow" size={16}/></Link>)}</div>;
}

export function QuestMeta({giver, location, chapter = 'I'}) {
  return <dl className="quest-meta"><div><dt>Zleceniodawca</dt><dd>{giver}</dd></div><div><dt>Miejsce</dt><dd>{location}</dd></div><div><dt>Rozdział</dt><dd>{chapter}</dd></div></dl>;
}

export function SourceNote({path}) {
  const {siteConfig: {customFields: {profile}}} = useDocusaurusContext();
  const sourcePath = path.split('/').map(encodeURIComponent).join('/');
  return <aside className="source-note"><Link href={`${profile.repository}/blob/${profile.branch}/docs/${sourcePath}`}>Materiał źródłowy <ArrowUpRight size={13}/></Link></aside>;
}

// Przykłady odsyłają do oryginalnych dokumentów NB do czasu właściwej migracji.
export function ExampleSourceNote({path}) {
  const {siteConfig: {customFields: {profile}}} = useDocusaurusContext();
  return profile.prototype ? <SourceNote path={path}/> : null;
}

export function ZoomFigure({src, alt, caption}) {
  const dialog = useRef(null);
  const image = useBaseUrl(src);
  return <figure className="wiki-figure">
    <button type="button" className="figure-trigger" onClick={() => dialog.current.showModal()} aria-label={`Powiększ: ${alt}`}><img src={image} alt={alt} loading="lazy"/><span><ZoomIn size={16}/> Powiększ mapę</span></button>
    <figcaption>{caption}</figcaption>
    <dialog className="image-dialog" ref={dialog} onClick={event => {if (event.target === event.currentTarget) dialog.current.close();}} aria-label={alt}>
      <button type="button" className="dialog-close" onClick={() => dialog.current.close()} aria-label="Zamknij podgląd obrazu"><X size={22}/></button><img src={image} alt={alt}/><p>{caption}</p>
    </dialog>
  </figure>;
}

export function Video({id, title}) {
  const [playing, setPlaying] = useState(false);
  return <div className="video-section"><div className="video-wrapper">{playing ? <iframe src={`https://www.youtube-nocookie.com/embed/${id}?autoplay=1`} title={title} referrerPolicy="strict-origin-when-cross-origin" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowFullScreen/> : <button type="button" onClick={() => setPlaying(true)} className="video-placeholder"><span className="play-icon"><Play size={25}/></span><strong>{title}</strong><span>Odtwórz poradnik wideo · YouTube <ExternalLink size={13}/></span></button>}</div><a className="video-external" href={`https://www.youtube.com/watch?v=${id}`} target="_blank" rel="noopener noreferrer">Otwórz na YouTube <ArrowUpRight size={13}/></a></div>;
}
