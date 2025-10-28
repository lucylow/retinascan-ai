import { serve } from "https://deno.land/std@0.168.0/http/server.ts";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const { image } = await req.json();
    
    if (!image) {
      return new Response(
        JSON.stringify({ error: "Image is required" }),
        { status: 400, headers: { ...corsHeaders, "Content-Type": "application/json" } }
      );
    }

    const LOVABLE_API_KEY = Deno.env.get("LOVABLE_API_KEY");
    if (!LOVABLE_API_KEY) {
      throw new Error("LOVABLE_API_KEY not configured");
    }

    // Call Lovable AI with vision model to analyze the retinal image
    const response = await fetch("https://ai.gateway.lovable.dev/v1/chat/completions", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${LOVABLE_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: "google/gemini-2.5-flash",
        messages: [
          {
            role: "system",
            content: `You are an expert ophthalmologist AI specialized in diabetic retinopathy detection. Analyze retinal fundus images and classify them into one of 5 severity levels:
0 - No DR (No Diabetic Retinopathy)
1 - Mild (Mild non-proliferative diabetic retinopathy)
2 - Moderate (Moderate non-proliferative diabetic retinopathy)
3 - Severe (Severe non-proliferative diabetic retinopathy)
4 - Proliferative DR (Proliferative diabetic retinopathy)

Respond ONLY with a JSON object in this exact format:
{
  "severity_class": <number 0-4>,
  "severity_level": "<No DR|Mild|Moderate|Severe|Proliferative DR>",
  "confidence": <decimal 0-1>,
  "label": "<full diagnosis label>",
  "recommendation": "<clinical recommendation>",
  "class_probabilities": {
    "class_0": <decimal 0-1>,
    "class_1": <decimal 0-1>,
    "class_2": <decimal 0-1>,
    "class_3": <decimal 0-1>,
    "class_4": <decimal 0-1>
  }
}`
          },
          {
            role: "user",
            content: [
              {
                type: "text",
                text: "Analyze this retinal fundus image for signs of diabetic retinopathy and provide a detailed diagnosis."
              },
              {
                type: "image_url",
                image_url: {
                  url: image
                }
              }
            ]
          }
        ],
        temperature: 0.1,
        max_tokens: 1000
      }),
    });

    if (response.status === 429) {
      return new Response(
        JSON.stringify({ error: "Rate limit exceeded. Please try again later." }),
        { status: 429, headers: { ...corsHeaders, "Content-Type": "application/json" } }
      );
    }

    if (response.status === 402) {
      return new Response(
        JSON.stringify({ error: "AI service payment required. Please add credits." }),
        { status: 402, headers: { ...corsHeaders, "Content-Type": "application/json" } }
      );
    }

    if (!response.ok) {
      const errorText = await response.text();
      console.error("AI gateway error:", response.status, errorText);
      throw new Error(`AI gateway error: ${response.status}`);
    }

    const aiResponse = await response.json();
    const content = aiResponse.choices?.[0]?.message?.content || "";
    
    // Extract JSON from the response
    const jsonMatch = content.match(/\{[\s\S]*\}/);
    if (!jsonMatch) {
      throw new Error("Failed to parse AI response");
    }

    const diagnosis = JSON.parse(jsonMatch[0]);

    return new Response(
      JSON.stringify(diagnosis),
      { headers: { ...corsHeaders, "Content-Type": "application/json" } }
    );

  } catch (error) {
    console.error("Error in analyze-retina:", error);
    return new Response(
      JSON.stringify({ error: error instanceof Error ? error.message : "Unknown error" }),
      { status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" } }
    );
  }
});
