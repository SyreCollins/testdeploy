export interface ModelResponse {
  text: string;
  provider: string;
  model: string;
  finish_reason: string;
  usage: Record<string, unknown> | null;
  raw: Record<string, unknown> | null;
}

export interface StreamEvent {
  type: "delta" | "done";
  text: string;
  finish_reason: string | null;
  usage: Record<string, unknown> | null;
}

export interface BaseModelProvider {
  provider_name: string;
  generate(
    prompt: string,
    system_prompt?: string | null,
    max_tokens?: number,
    temperature?: number,
  ): Promise<ModelResponse>;
  generateStream(
    prompt: string,
    system_prompt?: string | null,
    max_tokens?: number,
    temperature?: number,
  ): AsyncIterable<StreamEvent>;
}
