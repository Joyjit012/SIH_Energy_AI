import { z } from "zod";
import { COOKIE_NAME } from "@shared/const";
import { getSessionCookieOptions } from "./_core/cookies";
import { systemRouter } from "./_core/systemRouter";
import { publicProcedure, router } from "./_core/trpc";
import { ENV } from "./_core/env";

const polarOpsSystemPrompt = `You are PolarOps, an expert energy-management copilot for remote polar research stations.

Your job is to answer questions about load forecasting, renewable-energy integration, microgrid dispatch, battery strategy, generator scheduling, and fuel optimization under extreme polar conditions. Be practical, concise, and technically clear. Organize answers with short headings and bullets when useful.

Always reason about polar constraints such as long darkness, icing and snow accumulation, low-temperature battery derating, wind-turbine cut-out or icing risk, fuel logistics, generator warm-up and minimum-load limits, maintenance windows, thermal loads, communications outages, and the need for redundant power. When a question lacks site-specific data, state the assumptions and recommend the measurements or operational inputs needed to improve the answer. Distinguish planning guidance from a control command. Never invent sensor readings, weather forecasts, or station policies. Encourage verification by the station energy lead before changing live dispatch settings.

Use SI units and UTC when relevant. The interface may show illustrative demo telemetry for a generic polar station; do not treat it as a live control system. Give an actionable next step at the end of most answers.`;

async function invokeGemini(
  apiKey: string,
  messages: { role: string; content: string }[]
) {
  const contents = messages.map((m) => ({
    role: m.role === "assistant" ? "model" : "user",
    parts: [{ text: m.content }],
  }));

  const models = ["gemini-2.0-flash", "gemini-1.5-flash"];
  let lastError = "";

  for (const model of models) {
    try {
      const res = await fetch(
        `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${apiKey}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            system_instruction: {
              parts: [{ text: polarOpsSystemPrompt }],
            },
            contents,
          }),
        }
      );

      if (res.ok) {
        const data = await res.json();
        const text = data.candidates?.[0]?.content?.parts?.[0]?.text;
        if (text) return text;
      } else {
        lastError = await res.text();
      }
    } catch (e) {
      lastError = e instanceof Error ? e.message : String(e);
    }
  }

  throw new Error(`Gemini API call failed: ${lastError}`);
}

function fallbackAnswer(question: string) {
  const normalized = question.toLowerCase();
  if (normalized.includes("fuel") || normalized.includes("genset") || normalized.includes("diesel")) {
    return `## Fuel optimization starting point\n\nFor a generic polar station, keep the online genset(s) in their efficient loading band rather than chasing every short renewable fluctuation.`;
  }
  return `## A practical load-forecast frame\n\nStart with a 24-hour forecast at 15-minute or hourly resolution, then add an uncertainty band for polar conditions.`;
}

const chatMessageSchema = z.object({
  role: z.enum(["user", "assistant"]),
  content: z.string().min(1).max(8000),
});

export const appRouter = router({
  system: systemRouter,

  auth: router({
    me: publicProcedure.query((opts) => opts.ctx.user),

    logout: publicProcedure.mutation(({ ctx }) => {
      const cookieOptions = getSessionCookieOptions(ctx.req);

      ctx.res.clearCookie(COOKIE_NAME, {
        ...cookieOptions,
        maxAge: -1,
      });

      return { success: true } as const;
    }),
  }),

  ai: router({
    chat: publicProcedure
      .input(
        z.object({
          messages: z.array(chatMessageSchema).min(1).max(24),
        })
      )
      .mutation(async ({ input }) => {
        const lastQuestion = input.messages[input.messages.length - 1]?.content ?? "";
        const geminiKey = (
          process.env.GEMINI_API_KEY ||
          process.env.VITE_GEMINI_API_KEY ||
          ENV.geminiApiKey
        )?.trim();

        if (geminiKey) {
          try {
            const content = await invokeGemini(geminiKey, input.messages);
            return { content };
          } catch (error) {
            console.warn("[PolarOps] Gemini API error:", error);
            return {
              content: `Gemini API Error: ${
                error instanceof Error ? error.message : String(error)
              }`,
            };
          }
        }

        return {
          content: "Gemini API Key is missing. Please set GEMINI_API_KEY in Vercel Project Settings -> Environment Variables and redeploy.",
        };
      }),
  }),
});

export type AppRouter = typeof appRouter;