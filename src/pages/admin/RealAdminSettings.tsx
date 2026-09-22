import { Card, SectionHeading } from '../../components/common'

export function RealAdminSettings() {
  return <div><SectionHeading eyebrow="Workspace" title="Settings" description="Administrative settings are not enabled in this development authentication phase." /><Card><h2 className="heading">Configuration status</h2><p className="muted">No editable controls are shown because there is currently no backend settings resource. Operational values are managed through the application configuration and SQLite schema.</p></Card></div>
}