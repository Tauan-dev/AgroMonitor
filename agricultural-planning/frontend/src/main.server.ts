import { bootstrapApplication } from '@angular/platform-browser';
import { AppComponent } from './app/app.component';
import { config } from './app/app.config.server';

// The server rendering engine (CommonEngine) will call the exported bootstrap
// function with a BootstrapContext containing document/url/providers. We must
// forward that context to bootstrapApplication so the platform is properly
// created on the server. Otherwise Angular throws NG0401 (Missing Platform).
const bootstrap = (context?: unknown) => bootstrapApplication(AppComponent, config, context as any);

export default bootstrap;
