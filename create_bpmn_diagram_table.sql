CREATE TABLE "myapp_bpmndiagram" (
    "id" bigserial NOT NULL PRIMARY KEY,
    "name" varchar(255) NOT NULL,
    "description" text NULL,
    "xml" text NOT NULL,
    "created_at" timestamp with time zone NOT NULL,
    "updated_at" timestamp with time zone NOT NULL,
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED
);

CREATE INDEX "myapp_bpmndiagram_user_id_idx" ON "myapp_bpmndiagram" ("user_id");
CREATE INDEX "myapp_bpmndiagram_updated_at_idx" ON "myapp_bpmndiagram" ("updated_at");