import { createFileRoute, useNavigate, Link } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { toast } from "sonner";
import { Table2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { supabase } from "@/integrations/supabase/client";
import { useAuth } from "@/hooks/useAuth";

export const Route = createFileRoute("/auth")({
  head: () => ({
    meta: [
      { title: "Sign in — Excel Builder Studio" },
      {
        name: "description",
        content: "Sign in to design spreadsheet products and generate polished Excel workbooks.",
      },
      { property: "og:title", content: "Sign in — Excel Builder Studio" },
      {
        property: "og:description",
        content: "Access your workbook blueprints and build history.",
      },
    ],
  }),
  component: AuthPage,
});

function AuthPage() {
  const navigate = useNavigate();
  const { session, loading } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (!loading && session) navigate({ to: "/dashboard" });
  }, [session, loading, navigate]);

  async function signIn(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    const { error } = await supabase.auth.signInWithPassword({ email, password });
    setBusy(false);
    if (error) {
      toast.error(error.message);
      return;
    }
    navigate({ to: "/dashboard" });
  }

  async function signUp(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    const { error } = await supabase.auth.signUp({
      email,
      password,
      options: { emailRedirectTo: `${window.location.origin}/dashboard` },
    });
    setBusy(false);
    if (error) {
      toast.error(error.message);
      return;
    }
    toast.success("Account created — you can start building.");
    navigate({ to: "/dashboard" });
  }

  return (
    <main className="grid min-h-screen lg:grid-cols-2">
      <section className="hero-surface hidden flex-col justify-between p-12 lg:flex">
        <Link to="/" className="flex items-center gap-2 font-display text-lg font-semibold">
          <Table2 className="h-5 w-5" /> Excel Builder Studio
        </Link>
        <div className="max-w-md">
          <h1 className="text-4xl font-semibold">Blueprints in, workbooks out.</h1>
          <p className="mt-4 text-sm opacity-80">
            Define sheets, columns and KPIs once. The build engine renders themed, formula-wired
            .xlsx files on the server every time you ship a version.
          </p>
        </div>
        <p className="text-xs opacity-60">Ported from the Excel Product Engine architecture.</p>
      </section>

      <section className="flex items-center justify-center px-6 py-16">
        <div className="w-full max-w-sm">
          <h2 className="font-display text-2xl font-semibold">Welcome back</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Sign in or create an account to keep your products.
          </p>

          <Tabs defaultValue="signin" className="mt-8">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="signin">Sign in</TabsTrigger>
              <TabsTrigger value="signup">Create account</TabsTrigger>
            </TabsList>

            {(["signin", "signup"] as const).map((tab) => (
              <TabsContent key={tab} value={tab}>
                <form onSubmit={tab === "signin" ? signIn : signUp} className="space-y-4 pt-4">
                  <div className="space-y-2">
                    <Label htmlFor={`${tab}-email`}>Email</Label>
                    <Input
                      id={`${tab}-email`}
                      type="email"
                      required
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="you@company.com"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor={`${tab}-password`}>Password</Label>
                    <Input
                      id={`${tab}-password`}
                      type="password"
                      required
                      minLength={6}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="••••••••"
                    />
                  </div>
                  <Button type="submit" className="w-full" disabled={busy}>
                    {tab === "signin" ? "Sign in" : "Create account"}
                  </Button>
                </form>
              </TabsContent>
            ))}
          </Tabs>
        </div>
      </section>
    </main>
  );
}
